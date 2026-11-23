# Sentinel security verification

A mobile-first verification dashboard with a Python standard-library API and a
persistent SQLite event log. It sends trigger codes through Resend or SMTP.

## Run

Python 3.10+ is required. Set `ALERT_EMAIL` to the Gmail address that receives
codes, `PI_API_TOKEN` to a long random token shared with the Raspberry Pi, and
either `RESEND_API_KEY` (optionally `RESEND_FROM`) or SMTP settings. Start with:

```powershell
$env:ALERT_EMAIL = "you@gmail.com"
$env:PI_API_TOKEN = "replace-with-a-long-random-token"
$env:RESEND_API_KEY = "re_..."
python app.py
```

Open `http://localhost:8000`. The app creates `data/security.db` and a private
PIN-hashing key at first startup. Keep the `data` directory private and backed
up; set `APP_SECRET` to a stable, private secret if you manage secrets
externally. For local phone access on a trusted network, set `HOST=0.0.0.0` and
open `http://<computer-lan-ip>:8000`. Do not expose this development server
directly to the public internet; use HTTPS and a hardened reverse proxy.

In development, the footer's **Simulate Pi trigger** button is enabled by
default and uses the same email delivery as a real trigger. Set
`ENABLE_SIMULATION=false` to turn it off. Simulation is disabled automatically
when `APP_ENV=production`.

## Raspberry Pi API

Trigger a verification when the GPIO sensor fires:

```http
POST /api/trigger
Authorization: Bearer <PI_API_TOKEN>
```

The endpoint emails a randomly generated four-digit code and returns its
timestamp and expiry. It responds with `409` if another verification is
pending or still awaiting a Pi acknowledgement/reset. Email delivery failures
return `502` and do not leave a usable pending code.

Poll `GET /api/status` every two seconds. It returns `PENDING`, `VERIFIED`, or
`IDLE`; the Pi should send its OK GPIO output once when it first observes
`VERIFIED`. The dashboard's **Reset system to idle** action ends that event.
`POST /api/verify` accepts `{"pin":"1234"}` from the dashboard. Codes expire
after five minutes and are locked after five incorrect attempts.

`GET /api/history` returns the latest 20 event summaries. Codes are never
returned by any API. The trigger endpoint requires the Pi bearer token; status
and verification endpoints are intentionally available to the phone dashboard.

For SMTP instead of Resend, configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
`SMTP_PASSWORD`, and optionally `SMTP_FROM`. Gmail SMTP typically requires an
app password with 2-step verification enabled.
