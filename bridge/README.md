# INSAN Bridge

Local owner service. GitHub Pages cannot hold `XAI_API_KEY` or talk ONVIF, so this runs on your PC.

## What it does

- **SpaceXAI** — Mira, Vaani tutor, Study Assistant, NEXCODE AI call `http://127.0.0.1:8787/v1/chat`. The key never leaves this machine.
- **UniVista cameras** — paste an RTSP URL, or discover ONVIF on the LAN. ffmpeg turns the stream into MJPEG the browser can show.
- **NEXCODE rooms** — maps a 6-digit pair code to a PeerJS id and a file snapshot so a real phone can join.

## Start

1. Copy `.env.example` to `.env` and paste `XAI_API_KEY` (https://console.x.ai).
2. Double-click `Open-INSAN-Bridge.bat`.
3. Open an INSAN app. It looks for the bridge at `http://127.0.0.1:8787`.
4. On a phone (same Wi-Fi), set the bridge URL to `http://YOUR-PC-LAN-IP:8787` (printed in this window).

ONVIF SOAP (optional): `pip install -r requirements.txt`

ffmpeg is required for RTSP. A phone cannot reach your cameras unless this process is running and the phone is on the same network.
