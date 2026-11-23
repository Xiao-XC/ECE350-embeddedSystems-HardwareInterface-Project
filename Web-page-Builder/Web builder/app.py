import hashlib
import hmac
import json
import os
import secrets
import smtplib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "security.db"
SECRET_PATH = DATA_DIR / "app_secret.key"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
APP_ENV = os.environ.get("APP_ENV", "development").lower()
SIMULATION_ENABLED = os.environ.get(
    "ENABLE_SIMULATION", "true" if APP_ENV != "production" else "false"
).lower() in ("1", "true", "yes")
PIN_LIFETIME_SECONDS = 5 * 60
MAX_ATTEMPTS = 5


def utc_now():
    return datetime.now(timezone.utc)


def isoformat(value):
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_secret():
    configured_secret = os.environ.get("APP_SECRET")
    if configured_secret:
        return configured_secret.encode("utf-8")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SECRET_PATH.exists():
        try:
            with SECRET_PATH.open("xb") as secret_file:
                secret_file.write(secrets.token_bytes(32))
        except FileExistsError:
            pass
    if os.name != "nt":
        os.chmod(SECRET_PATH, 0o600)
    return SECRET_PATH.read_bytes()


def pin_digest(pin):
    return hmac.new(get_secret(), pin.encode("ascii"), hashlib.sha256).hexdigest()


@contextmanager
def connect_db():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    get_secret()
    with connect_db() as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pin_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                verified_at TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                email_status TEXT NOT NULL DEFAULT 'PENDING',
                response_ms INTEGER
            )
            """
        )


def send_alert_email(pin, expires_at):
    recipient = os.environ.get("ALERT_EMAIL")
    if not recipient:
        raise RuntimeError("Set ALERT_EMAIL to the Gmail address that should receive PINs.")

    subject = "Security verification code"
    text = (
        "A security sensor was triggered.\n\n"
        f"Your verification code is {pin}.\n"
        f"It expires at {expires_at}.\n\n"
        "If you did not expect this alert, do not share the code."
    )
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        sender = os.environ.get("RESEND_FROM", "Security Verification <onboarding@resend.dev>")
        payload = json.dumps(
            {"from": sender, "to": [recipient], "subject": subject, "text": text}
        ).encode("utf-8")
        request = Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=15) as response:
                if response.status >= 300:
                    raise RuntimeError(f"Email provider returned HTTP {response.status}.")
        except HTTPError as error:
            raise RuntimeError(f"Email provider returned HTTP {error.code}.") from error
        except URLError as error:
            raise RuntimeError(f"Could not reach the email provider: {error.reason}.") from error
        return

    smtp_host = os.environ.get("SMTP_HOST")
    if smtp_host:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", ""))
        message["To"] = recipient
        message.set_content(text)
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as client:
                if os.environ.get("SMTP_USER"):
                    client.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
                client.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as client:
                client.starttls()
                if os.environ.get("SMTP_USER"):
                    client.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
                client.send_message(message)
        return

    raise RuntimeError("Configure RESEND_API_KEY or SMTP_HOST to send verification emails.")


def expire_pending(connection, event):
    if event and event["status"] == "PENDING" and parse_time(event["expires_at"]) <= utc_now():
        connection.execute("UPDATE events SET status = 'EXPIRED' WHERE id = ?", (event["id"],))
        return "EXPIRED"
    return event["status"] if event else None


def create_trigger():
    created = utc_now()
    expires = created + timedelta(seconds=PIN_LIFETIME_SECONDS)
    pin = f"{secrets.randbelow(10000):04d}"
    with connect_db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        latest = connection.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1").fetchone()
        current_status = expire_pending(connection, latest)
        if current_status in ("PENDING", "VERIFIED"):
            connection.rollback()
            raise ValueError("A verification is already active. Reset the system before triggering again.")
        cursor = connection.execute(
            """
            INSERT INTO events (pin_hash, status, created_at, expires_at)
            VALUES (?, 'PENDING', ?, ?)
            """,
            (pin_digest(pin), isoformat(created), isoformat(expires)),
        )
        event_id = cursor.lastrowid

    try:
        send_alert_email(pin, isoformat(expires))
    except Exception as error:
        with connect_db() as connection:
            connection.execute(
                "UPDATE events SET status = 'EMAIL_FAILED', email_status = 'FAILED' WHERE id = ?",
                (event_id,),
            )
        raise RuntimeError(str(error)) from error

    with connect_db() as connection:
        connection.execute("UPDATE events SET email_status = 'SENT' WHERE id = ?", (event_id,))
    return {"id": event_id, "status": "PENDING", "timestamp": isoformat(created),
            "expiresAt": isoformat(expires)}


def get_status():
    with connect_db() as connection:
        event = connection.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1").fetchone()
        resulting_status = expire_pending(connection, event)
        if not event:
            return {"status": "IDLE", "timestamp": None}
        if resulting_status == "PENDING":
            return {
                "status": "PENDING",
                "timestamp": event["created_at"],
                "expiresAt": event["expires_at"],
                "id": event["id"],
                "attemptsRemaining": max(0, MAX_ATTEMPTS - event["attempts"]),
            }
        if resulting_status == "VERIFIED":
            return {"status": "VERIFIED", "timestamp": event["verified_at"], "id": event["id"]}
        return {
            "status": "IDLE",
            "timestamp": event["created_at"],
            "lastResult": resulting_status,
            "id": event["id"],
        }


def verify_pin(pin):
    with connect_db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        event = connection.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1").fetchone()
        status = expire_pending(connection, event)
        if not event or status != "PENDING":
            connection.commit()
            return {"ok": False, "reason": "EXPIRED", "message": "There is no active code."}

        if not hmac.compare_digest(pin_digest(pin), event["pin_hash"]):
            attempts = event["attempts"] + 1
            locked = attempts >= MAX_ATTEMPTS
            connection.execute(
                "UPDATE events SET attempts = ?, status = ? WHERE id = ?",
                (attempts, "LOCKED" if locked else "PENDING", event["id"]),
            )
            connection.commit()
            return {
                "ok": False,
                "reason": "LOCKED" if locked else "INVALID",
                "message": "Too many incorrect attempts." if locked else "Incorrect code. Try again.",
                "attemptsRemaining": max(0, MAX_ATTEMPTS - attempts),
            }

        verified_at = utc_now()
        response_ms = max(0, int((verified_at - parse_time(event["created_at"])).total_seconds() * 1000))
        connection.execute(
            """
            UPDATE events SET status = 'VERIFIED', verified_at = ?, response_ms = ?
            WHERE id = ?
            """,
            (isoformat(verified_at), response_ms, event["id"]),
        )
        connection.commit()
        return {"ok": True, "status": "VERIFIED", "timestamp": isoformat(verified_at)}


def reset_system():
    with connect_db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        event = connection.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1").fetchone()
        if not event or event["status"] != "VERIFIED":
            connection.rollback()
            raise ValueError("The system can only be reset after successful verification.")
        connection.execute("UPDATE events SET status = 'RESET' WHERE id = ?", (event["id"],))


def history():
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT id, status, created_at, verified_at, response_ms, email_status
            FROM events ORDER BY id DESC LIMIT 20
            """
        ).fetchall()
    return [
        {
            "id": row["id"],
            "status": row["status"],
            "timestamp": row["created_at"],
            "verifiedAt": row["verified_at"],
            "responseMs": row["response_ms"],
            "emailStatus": row["email_status"],
        }
        for row in rows
    ]


class Handler(BaseHTTPRequestHandler):
    server_version = "SecureVerify/1.0"

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {format_string % args}")

    def send_json(self, status_code, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 4096:
                raise ValueError
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError
            return body
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "A valid JSON object is required."})
            return None

    def authorized_pi(self):
        token = os.environ.get("PI_API_TOKEN")
        if not token:
            return False
        supplied = self.headers.get("Authorization", "")
        prefix = "Bearer "
        return supplied.startswith(prefix) and supplied[len(prefix):].isascii() and hmac.compare_digest(
            supplied[len(prefix):], token
        )

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(200, get_status())
        elif self.path == "/api/history":
            self.send_json(200, {"events": history()})
        elif self.path == "/api/config":
            self.send_json(200, {"simulationEnabled": SIMULATION_ENABLED})
        elif self.path == "/" or self.path == "/index.html":
            self.serve_file("index.html", "text/html; charset=utf-8")
        elif self.path == "/styles.css":
            self.serve_file("styles.css", "text/css; charset=utf-8")
        elif self.path == "/app.js":
            self.serve_file("app.js", "text/javascript; charset=utf-8")
        else:
            self.send_json(404, {"error": "Not found."})

    def do_POST(self):
        if self.path == "/api/trigger":
            if not self.authorized_pi():
                self.send_json(401, {"error": "A valid Raspberry Pi bearer token is required."})
                return
        elif self.path == "/api/simulate":
            if not SIMULATION_ENABLED:
                self.send_json(404, {"error": "Simulation is disabled."})
                return
        elif self.path == "/api/verify":
            body = self.read_json()
            if body is None:
                return
            pin = body.get("pin")
            if not isinstance(pin, str) or len(pin) != 4 or not pin.isascii() or not pin.isdigit():
                self.send_json(400, {"error": "Enter a four-digit code."})
                return
            result = verify_pin(pin)
            self.send_json(200 if result["ok"] else 400, result)
            return
        elif self.path == "/api/reset":
            if self.headers.get("X-Requested-With") != "SentinelDashboard":
                self.send_json(403, {"error": "A dashboard request is required."})
                return
            try:
                reset_system()
            except ValueError as error:
                self.send_json(409, {"error": str(error)})
                return
            self.send_json(200, {"status": "IDLE"})
            return
        else:
            self.send_json(404, {"error": "Not found."})
            return

        if self.path in ("/api/trigger", "/api/simulate"):
            if self.headers.get("Content-Length", "0") not in ("0", ""):
                body = self.read_json()
                if body is None:
                    return
            try:
                result = create_trigger()
            except ValueError as error:
                self.send_json(409, {"error": str(error)})
            except RuntimeError as error:
                self.send_json(502, {"error": str(error)})
            else:
                self.send_json(201, result)

    def serve_file(self, name, content_type):
        file_path = ROOT / "public" / name
        try:
            content = file_path.read_bytes()
        except OSError:
            self.send_json(404, {"error": "Static file not found."})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    initialize_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Security verification dashboard listening on http://{HOST}:{PORT}")
    print("Set PI_API_TOKEN and ALERT_EMAIL, then configure Resend or SMTP for email delivery.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
