"""Build silent visual showcase MP4s from live app screenshots."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "_shots"
BUILD = ROOT / "_build" / "showcase"
ICONS = ROOT.parent / "icons"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FFMPEG = Path(
    r"C:\Users\shamu\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
)
W, H = 1280, 720
FONT = Path(r"C:\Windows\Fonts\segoeuib.ttf")
FONT2 = Path(r"C:\Windows\Fonts\segoeui.ttf")

SHOWCASES = [
    {
        "id": "jarvis",
        "title": "J.A.R.V.I.S",
        "accent": (62, 200, 232),
        "icon": ICONS / "jarvis-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/insan-creations/products/jarvis.html", "Product page"),
            ("https://sl8722569-ux.github.io/jarvis-assitant/webapp/", "Web app"),
        ],
    },
    {
        "id": "study-assistant",
        "title": "AI Study Assistant",
        "accent": (212, 160, 23),
        "icon": ICONS / "study-assistant-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/insan-creations/products/study-assistant.html", "Product page"),
            ("https://sl8722569-ux.github.io/ai-study-assistant/web/", "Study app"),
        ],
    },
    {
        "id": "univista",
        "title": "UniVista",
        "accent": (62, 200, 232),
        "icon": ICONS / "univista-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/univista/", "Official site"),
            ("https://sl8722569-ux.github.io/univista/web/", "Early Access app"),
        ],
    },
    {
        "id": "vaani",
        "title": "Vaani",
        "accent": (232, 184, 74),
        "icon": ICONS / "language-ai-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/universal-language-ai/", "Official site"),
            ("https://sl8722569-ux.github.io/universal-language-ai/web/", "Learn · catalogue · tutor"),
        ],
    },
    {
        "id": "nexcode",
        "title": "NEXCODE",
        "accent": (0, 120, 212),
        "icon": ICONS / "nexcode-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/nexcode/", "Official site"),
            ("https://sl8722569-ux.github.io/nexcode/web/", "Host editor"),
        ],
    },
    {
        "id": "insan-creations",
        "title": "INSAN CREATIONS",
        "accent": (212, 160, 23),
        "icon": ICONS / "insan-creations-192.png",
        "shots": [
            ("https://sl8722569-ux.github.io/insan-creations/", "Studio home"),
            ("https://sl8722569-ux.github.io/insan-creations/apps.html", "All apps"),
            ("https://sl8722569-ux.github.io/insan-creations/tutorials.html", "Tutorials"),
        ],
    },
]


def screenshot(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    profile = ROOT / "_chrome" / dest.stem
    profile.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1280,800",
        f"--user-data-dir={profile}",
        "--virtual-time-budget=9000",
        f"--screenshot={dest}",
        url,
    ]
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
        return dest.exists() and dest.stat().st_size > 1000
    except Exception:
        return False


def caption(src: Path, label: str, title: str, accent: tuple, icon: Path, dest: Path) -> None:
    im = Image.open(src).convert("RGB")
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, H - 92, W, H), fill=(0, 0, 0, 170))
    f1 = ImageFont.truetype(str(FONT), 28)
    f2 = ImageFont.truetype(str(FONT2), 18)
    if icon.exists():
        ic = Image.open(icon).convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
        overlay.paste(ic, (28, H - 70), ic)
    d.text((90, H - 78), title, font=f1, fill=accent + (255,))
    d.text((90, H - 44), "SHOWCASE  ·  " + label, font=f2, fill=(220, 220, 220, 255))
    Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB").save(dest, quality=92)


def title_card(title: str, accent: tuple, icon: Path, dest: Path) -> None:
    img = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(str(FONT), 56)
    f2 = ImageFont.truetype(str(FONT2), 24)
    if icon.exists():
        ic = Image.open(icon).convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
        img.paste(ic, (80, 240), ic)
    d.text((200, 250), title, font=f1, fill=accent)
    d.text((200, 330), "Showcase  ·  INSAN CREATIONS", font=f2, fill=(160, 160, 160))
    img.save(dest, quality=92)


def still(image: Path, seconds: float, out: Path, zoom: bool) -> None:
    frames = int(30 * seconds)
    vf = f"scale={W}:{H},format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={seconds-0.25}:d=0.25"
    if zoom:
        vf = (
            f"scale=1400:788,zoompan=z='min(zoom+0.0012,1.08)':x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,format=yuv420p,"
            f"fade=t=in:st=0:d=0.25,fade=t=out:st={seconds-0.25}:d=0.25"
        )
    subprocess.check_call(
        [str(FFMPEG), "-y", "-loop", "1", "-i", str(image), "-t", f"{seconds:.2f}",
         "-vf", vf, "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def concat(clips: list[Path], out: Path) -> None:
    lst = BUILD / (out.stem + ".txt")
    lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    subprocess.check_call(
        [str(FFMPEG), "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def build(spec: dict) -> Path:
    work = BUILD / spec["id"]
    work.mkdir(parents=True, exist_ok=True)
    clips = []
    title = work / "title.jpg"
    title_card(spec["title"], spec["accent"], spec["icon"], title)
    tclip = work / "title.mp4"
    still(title, 2.4, tclip, False)
    clips.append(tclip)
    for i, (url, label) in enumerate(spec["shots"]):
        raw = SHOTS / f"{spec['id']}-{i}.png"
        if not raw.exists() or raw.stat().st_size < 1000:
            print("shot", url)
            if not screenshot(url, raw):
                print("  fail", url)
                continue
        cap = work / f"c{i}.jpg"
        caption(raw, label, spec["title"], spec["accent"], spec["icon"], cap)
        clip = work / f"c{i}.mp4"
        still(cap, 4.2, clip, True)
        clips.append(clip)
    out = ROOT / f"showcase-{spec['id']}.mp4"
    concat(clips, out)
    print("built", out, out.stat().st_size)
    return out


def main() -> int:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    SHOTS.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    for spec in SHOWCASES:
        if only and spec["id"] != only:
            continue
        build(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
