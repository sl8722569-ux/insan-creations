#!/usr/bin/env python3
"""INSAN Bridge — local owner service (not GitHub Pages).

Provides:
  - SpaceXAI proxy (XAI_API_KEY stays on this machine)
  - RTSP / ONVIF camera streams for UniVista (ffmpeg → MJPEG)
  - NEXCODE pairing rooms (short code → WebRTC/PeerJS id + file snapshot)

Binds LAN so a phone on the same Wi-Fi can reach it.
Never put XAI_API_KEY in a website.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("INSAN_BRIDGE_PORT", "8787"))
HOST = os.environ.get("INSAN_BRIDGE_HOST", "0.0.0.0")
MODEL = os.environ.get("XAI_MODEL", "grok-4.6")
XAI_URL = "https://api.x.ai/v1/chat/completions"

LOCK = threading.Lock()
CAMERAS: dict[str, dict] = {}
ROOMS: dict[str, dict] = {}


def load_dotenv() -> None:
    for path in (ROOT / ".env", Path.home() / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def which_ffmpeg() -> str | None:
    from shutil import which

    p = which("ffmpeg")
    if p:
        return p
    winget = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
    if winget.exists():
        for f in winget.rglob("ffmpeg.exe"):
            return str(f)
    return None


def lan_ips() -> list[str]:
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except OSError:
        pass
    return ips


def api_key() -> str:
    return (os.environ.get("XAI_API_KEY") or "").strip()


def cors(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Cache-Control", "no-store")


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    n = int(handler.headers.get("Content-Length") or 0)
    if n <= 0:
        return {}
    raw = handler.rfile.read(n)
    try:
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def send_json(handler: BaseHTTPRequestHandler, code: int, obj: dict) -> None:
    body = json.dumps(obj).encode("utf-8")
    handler.send_response(code)
    cors(handler)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def xai_chat(messages: list[dict], system: str) -> str:
    key = api_key()
    if not key:
        raise RuntimeError("XAI_API_KEY is not set on this PC. Put it in INSAN-CREATIONS/bridge/.env")
    payload = {
        "model": MODEL,
        "messages": ([{"role": "system", "content": system}] if system else []) + messages,
        "temperature": 0.4,
    }
    req = Request(
        XAI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "INSAN-Bridge",
        },
        method="POST",
    )
    with urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("SpaceXAI returned no choices")
    return ((choices[0].get("message") or {}).get("content") or "").strip()


def ws_discover(timeout: float = 3.0) -> list[dict]:
    probe = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"'
        ' xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"'
        ' xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"'
        ' xmlns:dn="http://www.onvif.org/ver10/network/wsdl">'
        "<e:Header><w:MessageID>uuid:" + str(uuid.uuid4()) + "</w:MessageID>"
        "<w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>"
        "<w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action></e:Header>"
        "<e:Body><d:Probe><d:Types>dn:NetworkVideoTransmitter</d:Types></d:Probe></e:Body></e:Envelope>"
    ).encode("utf-8")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    found: dict[str, dict] = {}
    try:
        sock.sendto(probe, ("239.255.255.250", 3702))
        end = time.time() + timeout
        while time.time() < end:
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                break
            text = data.decode("utf-8", errors="ignore")
            xaddr = ""
            low = text.lower()
            if "xaddrs>" in low:
                i = low.find("xaddrs>")
                j = text.find("<", i + 7)
                xaddr = text[i + 7 : j].strip() if j > i else ""
            found[addr[0]] = {"ip": addr[0], "xaddrs": xaddr, "raw_len": len(data)}
    finally:
        sock.close()
    return list(found.values())


def onvif_rtsp(host: str, username: str, password: str) -> str:
    try:
        from onvif import ONVIFCamera  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "ONVIF library not installed. pip install onvif-zeep  — or paste an RTSP URL instead."
        ) from e
    ip = host
    port = 80
    if "://" in host:
        u = urlparse(host)
        ip = u.hostname or host
        port = u.port or 80
    cam = ONVIFCamera(ip, port, username, password)
    media = cam.create_media_service()
    profiles = media.GetProfiles()
    if not profiles:
        raise RuntimeError("ONVIF camera has no media profiles")
    token = profiles[0].token
    req = media.create_type("GetStreamUri")
    req.ProfileToken = token
    req.StreamSetup = {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
    uri = media.GetStreamUri(req).Uri
    if username and "://" in uri and "@" not in uri:
        head, tail = uri.split("://", 1)
        uri = f"{head}://{username}:{password}@{tail}"
    return uri


def start_ffmpeg(rtsp: str) -> subprocess.Popen:
    ff = which_ffmpeg()
    if not ff:
        raise RuntimeError("ffmpeg not found. Install FFmpeg and retry.")
    cmd = [
        ff,
        "-hide_banner",
        "-loglevel",
        "error",
        "-rtsp_transport",
        "tcp",
        "-i",
        rtsp,
        "-an",
        "-q:v",
        "6",
        "-r",
        "10",
        "-f",
        "mpjpeg",
        "-boundary_tag",
        "ffmpeg",
        "pipe:1",
    ]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[bridge] " + (fmt % args) + "\n")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        cors(self)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        q = parse_qs(parsed.query)
        if path in ("/", "/health"):
            send_json(
                self,
                200,
                {
                    "ok": True,
                    "service": "insan-bridge",
                    "ai": bool(api_key()),
                    "model": MODEL if api_key() else None,
                    "ffmpeg": bool(which_ffmpeg()),
                    "lan": lan_ips(),
                    "port": PORT,
                    "cameras": list(CAMERAS.keys()),
                    "rooms": list(ROOMS.keys()),
                },
            )
            return
        if path == "/lan":
            send_json(self, 200, {"ok": True, "lan": lan_ips(), "port": PORT})
            return
        if path == "/onvif/discover":
            try:
                items = ws_discover()
                send_json(self, 200, {"ok": True, "devices": items})
            except Exception as e:
                send_json(self, 500, {"ok": False, "error": str(e)})
            return
        if path == "/onvif/cameras":
            with LOCK:
                info = {
                    k: {"id": k, "name": v.get("name"), "kind": v.get("kind")}
                    for k, v in CAMERAS.items()
                }
            send_json(self, 200, {"ok": True, "cameras": info})
            return
        if path.startswith("/stream/") and path.endswith(".mjpg"):
            cam_id = path[len("/stream/") : -len(".mjpg")]
            self._mjpeg(cam_id)
            return
        if path == "/nexcode/room":
            code = (q.get("code") or [""])[0]
            with LOCK:
                room = ROOMS.get(code)
            if not room:
                send_json(self, 404, {"ok": False, "error": "unknown room"})
                return
            send_json(self, 200, {"ok": True, "room": room})
            return
        send_json(self, 404, {"ok": False, "error": "unknown route"})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/onvif/cameras/"):
            cam_id = parsed.path.rsplit("/", 1)[-1]
            self._stop_cam(cam_id)
            send_json(self, 200, {"ok": True})
            return
        send_json(self, 404, {"ok": False, "error": "unknown route"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = read_json(self)
        if path == "/v1/chat":
            self._chat(body)
            return
        if path == "/onvif/connect":
            self._connect_cam(body)
            return
        if path == "/nexcode/room":
            code = str(body.get("code") or "").strip()
            if not code:
                send_json(self, 400, {"ok": False, "error": "code required"})
                return
            with LOCK:
                room = ROOMS.get(code) or {"code": code, "created": time.time()}
                for k in ("peerId", "role", "files", "current", "updated"):
                    if k in body:
                        room[k] = body[k]
                room["updated"] = time.time()
                ROOMS[code] = room
            send_json(self, 200, {"ok": True, "room": room})
            return
        send_json(self, 404, {"ok": False, "error": "unknown route"})

    def _chat(self, body: dict) -> None:
        app = str(body.get("app") or "studio")
        user_messages = body.get("messages") or []
        if not isinstance(user_messages, list) or not user_messages:
            send_json(self, 400, {"ok": False, "error": "messages required"})
            return
        clean = []
        for m in user_messages:
            if not isinstance(m, dict):
                continue
            role = m.get("role") if m.get("role") in ("user", "assistant", "system") else "user"
            content = str(m.get("content") or "")[:8000]
            if content:
                clean.append({"role": role, "content": content})
        if not clean:
            send_json(self, 400, {"ok": False, "error": "empty messages"})
            return
        system = str(body.get("system") or "").strip()
        if not system:
            system = {
                "mira": "You are Mira, UniVista's assistant from INSAN CREATIONS. Be warm and honest. This device camera and LAN cameras via INSAN Bridge work. Do not claim ONVIF cameras exist if the user has not connected them. Do not invent detections.",
                "study": "You are the AI Study Assistant from INSAN CREATIONS. Teach clearly. Not official exam papers. Match the student's board/grade if given.",
                "vaani": "You are Vaani's tutor from INSAN CREATIONS. Keep languages and scripts separate. Do not invent vocabulary for low-resource languages. Do not claim 800 live courses.",
                "nexcode": "You are NEX, the NEXCODE helper from INSAN CREATIONS. Help with code in the editor. No API keys in the browser. Be concise.",
            }.get(app, "You are an INSAN CREATIONS assistant. Be accurate. Do not overclaim product features.")
        try:
            text = xai_chat(clean[-12:], system)
            send_json(self, 200, {"ok": True, "text": text, "model": MODEL, "app": app})
        except Exception as e:
            send_json(self, 502, {"ok": False, "error": str(e)})

    def _connect_cam(self, body: dict) -> None:
        name = str(body.get("name") or "Camera")[:40]
        rtsp = str(body.get("rtsp") or "").strip()
        host = str(body.get("host") or "").strip()
        user = str(body.get("user") or "")
        password = str(body.get("password") or "")
        kind = "rtsp"
        try:
            if not rtsp and host:
                rtsp = onvif_rtsp(host, user, password)
                kind = "onvif"
            if not rtsp:
                send_json(self, 400, {"ok": False, "error": "Provide rtsp or ONVIF host"})
                return
            proc = start_ffmpeg(rtsp)
            cam_id = "cam" + str(int(time.time() * 1000))[-8:]
            with LOCK:
                CAMERAS[cam_id] = {
                    "id": cam_id,
                    "name": name,
                    "kind": kind,
                    "proc": proc,
                    "rtsp": rtsp,
                }
            send_json(
                self,
                200,
                {
                    "ok": True,
                    "id": cam_id,
                    "name": name,
                    "kind": kind,
                    "mjpeg": f"/stream/{cam_id}.mjpg",
                },
            )
        except Exception as e:
            send_json(self, 500, {"ok": False, "error": str(e)})

    def _stop_cam(self, cam_id: str) -> None:
        with LOCK:
            cam = CAMERAS.pop(cam_id, None)
        if cam and cam.get("proc"):
            try:
                cam["proc"].kill()
            except OSError:
                pass

    def _mjpeg(self, cam_id: str) -> None:
        with LOCK:
            cam = CAMERAS.get(cam_id)
        if not cam or not cam.get("proc") or not cam["proc"].stdout:
            send_json(self, 404, {"ok": False, "error": "no such stream"})
            return
        proc: subprocess.Popen = cam["proc"]
        self.send_response(200)
        cors(self)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=ffmpeg")
        self.end_headers()
        try:
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


def main() -> None:
    load_dotenv()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    ips = lan_ips()
    print("INSAN Bridge  http://127.0.0.1:%s/" % PORT)
    for ip in ips:
        print("  LAN         http://%s:%s/" % (ip, PORT))
    print("  SpaceXAI    %s" % ("ready (" + MODEL + ")" if api_key() else "OFF — set XAI_API_KEY in .env"))
    print("  ffmpeg      %s" % (which_ffmpeg() or "missing"))
    print("  health      http://127.0.0.1:%s/health" % PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        with LOCK:
            for cam in list(CAMERAS.values()):
                try:
                    cam["proc"].kill()
                except Exception:
                    pass
        httpd.server_close()


if __name__ == "__main__":
    main()
