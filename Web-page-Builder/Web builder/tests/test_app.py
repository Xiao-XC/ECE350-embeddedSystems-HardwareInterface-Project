import tempfile
import json
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import app


class SecurityWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name)
        self.settings = (
            patch.object(app, "DATA_DIR", self.data_path),
            patch.object(app, "DB_PATH", self.data_path / "security.db"),
            patch.object(app, "SECRET_PATH", self.data_path / "app_secret.key"),
            patch.dict(app.os.environ, {"APP_SECRET": "test-only-secret"}),
        )
        for setting in self.settings:
            setting.start()
        app.initialize_db()
        self.email = patch.object(app, "send_alert_email")
        self.send_email = self.email.start()

    def tearDown(self):
        self.email.stop()
        for setting in reversed(self.settings):
            setting.stop()
        self.temp_dir.cleanup()

    def test_code_is_emailed_verified_and_not_returned_by_status(self):
        event = app.create_trigger()
        pin = self.send_email.call_args.args[0]
        self.assertRegex(pin, r"^\d{4}$")
        self.assertEqual(event["status"], "PENDING")
        self.assertEqual(app.get_status()["status"], "PENDING")

        result = app.verify_pin(pin)

        self.assertTrue(result["ok"])
        self.assertEqual(app.get_status()["status"], "VERIFIED")
        self.assertNotIn(pin, str(app.get_status()))

    def test_wrong_code_locks_after_five_attempts(self):
        app.create_trigger()

        for attempt in range(app.MAX_ATTEMPTS - 1):
            result = app.verify_pin("not-a-pin")
            self.assertEqual(result["reason"], "INVALID")
            self.assertEqual(result["attemptsRemaining"], app.MAX_ATTEMPTS - attempt - 1)

        result = app.verify_pin("not-a-pin")

        self.assertEqual(result["reason"], "LOCKED")
        self.assertEqual(app.get_status()["lastResult"], "LOCKED")

    def test_expired_code_returns_system_to_idle(self):
        app.create_trigger()
        with app.connect_db() as connection:
            connection.execute(
                "UPDATE events SET expires_at = '2000-01-01T00:00:00Z'"
            )

        result = app.get_status()

        self.assertEqual(result["status"], "IDLE")
        self.assertEqual(result["lastResult"], "EXPIRED")

    def test_cannot_create_another_trigger_while_verification_is_pending(self):
        app.create_trigger()

        with self.assertRaises(ValueError):
            app.create_trigger()

        self.assertEqual(self.send_email.call_count, 1)

    def test_email_failure_does_not_leave_a_pending_code(self):
        self.send_email.side_effect = RuntimeError("Email delivery failed.")

        with self.assertRaises(RuntimeError):
            app.create_trigger()

        self.assertEqual(app.get_status()["status"], "IDLE")
        self.assertEqual(app.get_status()["lastResult"], "EMAIL_FAILED")

    def test_reset_only_after_verification(self):
        app.create_trigger()
        with self.assertRaises(ValueError):
            app.reset_system()
        app.verify_pin(self.send_email.call_args.args[0])

        app.reset_system()

        self.assertEqual(app.get_status()["status"], "IDLE")
        self.assertEqual(app.history()[0]["status"], "RESET")

    def test_api_protects_pi_trigger_and_serves_verified_status(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with patch.dict(app.os.environ, {"PI_API_TOKEN": "test-token"}):
                unauthorized = Request(f"{base_url}/api/trigger", data=b"{}")
                with self.assertRaises(HTTPError) as error:
                    urlopen(unauthorized)
                self.assertEqual(error.exception.code, 401)

                trigger = Request(
                    f"{base_url}/api/trigger",
                    data=b"{}",
                    headers={"Authorization": "Bearer test-token"},
                )
                with urlopen(trigger) as response:
                    self.assertEqual(response.status, 201)
                pin = self.send_email.call_args.args[0]

                verify = Request(
                    f"{base_url}/api/verify",
                    data=json.dumps({"pin": pin}).encode(),
                    headers={"Content-Type": "application/json"},
                )
                with urlopen(verify) as response:
                    self.assertEqual(json.loads(response.read())["status"], "VERIFIED")
                with urlopen(f"{base_url}/api/status") as response:
                    self.assertEqual(json.loads(response.read())["status"], "VERIFIED")
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
