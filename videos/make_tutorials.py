"""Build 4 INSAN CREATIONS tutorial MP4s (cards + Windows voice + ffmpeg)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "_frames"
BUILD = ROOT / "_build"
ICONS = ROOT.parent / "icons"
FFMPEG = Path(
    r"C:\Users\shamu\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
)
FFPROBE = FFMPEG.with_name("ffprobe.exe")
W, H = 1280, 720

FONTS = Path(r"C:\Windows\Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def rounded(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius, fill=255)
    im.putalpha(mask)
    return im


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> str:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def card(bg: tuple, accent: tuple, icon: Path | None, kicker: str, title: str, body: str, out: Path) -> None:
    img = Image.new("RGB", (W, H), bg)
    # faint vignette
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    sd.ellipse((-80, -80, W + 80, H + 80), fill=40)
    shade = shade.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(img, ImageEnhance.Brightness(img).enhance(1.12), shade)

    draw = ImageDraw.Draw(img)
    f_k = font("segoeui.ttf", 22)
    f_t = font("segoeuib.ttf", 48)
    f_b = font("segoeui.ttf", 32)
    x = 88
    y = 86
    if icon and icon.exists():
        ic = Image.open(icon).convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
        ic = rounded(ic, 22)
        img.paste(ic, (x, 48), ic)
        x = 88 + 96 + 22
        y = 58
    draw.text((x, y), kicker, font=f_k, fill=accent)
    title_wrapped = wrap(draw, title, f_t, W - 160)
    draw.multiline_text((88, 168), title_wrapped, font=f_t, fill=(242, 234, 216), spacing=8)
    body_wrapped = wrap(draw, body, f_b, W - 180)
    draw.multiline_text((88, 360), body_wrapped, font=f_b, fill=(180, 190, 200), spacing=10)
    draw.rectangle((88, H - 48, 88 + 220, H - 42), fill=accent)
    img.save(out, quality=95)


def tts(text: str, wav: Path) -> None:
    ps = BUILD / (wav.stem + ".ps1")
    # here-string so apostrophes in tutorial copy stay intact
    ps.write_text(
        "Add-Type -AssemblyName System.Speech\n"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer\n"
        "$s.Rate = -1\n"
        "$s.Volume = 100\n"
        "try { $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female) } catch {}\n"
        f'$s.SetOutputToWaveFile("{wav}")\n'
        "$s.Speak(@'\n"
        f"{text}\n"
        "'@)\n"
        "$s.Dispose()\n",
        encoding="utf-8",
    )
    subprocess.check_call(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def still_to_mp4(image: Path, seconds: float, out: Path, zoom: bool = False) -> None:
    seconds = max(3.2, seconds)
    vf = f"scale={W}:{H},format=yuv420p,fade=t=in:st=0:d=0.35,fade=t=out:st={seconds-0.35}:d=0.35"
    if zoom:
        # ~30fps * duration frames
        frames = int(30 * seconds)
        vf = (
            f"scale=1440:810,zoompan=z='min(zoom+0.0009,1.10)':x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,format=yuv420p,"
            f"fade=t=in:st=0:d=0.35,fade=t=out:st={seconds-0.35}:d=0.35"
        )
    subprocess.check_call(
        [
            str(FFMPEG),
            "-y",
            "-loop",
            "1",
            "-i",
            str(image),
            "-t",
            f"{seconds:.2f}",
            "-vf",
            vf,
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def concat(clips: list[Path], audio: Path, out: Path) -> None:
    lst = BUILD / (out.stem + "_list.txt")
    lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    subprocess.check_call(
        [
            str(FFMPEG),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


TUTORIALS = [
    {
        "id": "jarvis",
        "accent": (62, 200, 232),
        "bg": (7, 16, 24),
        "icon": ICONS / "jarvis-192.png",
        "hero": FRAMES / "jarvis.jpg",
        "slides": [
            ("INSAN CREATIONS TUTORIAL", "J.A.R.V.I.S", "How to open, talk, and stay in control of privacy.",
             "This is a short tutorial for Jarvis, your personal assistant from Insan Creations."),
            ("STEP 1", "Open the app", "On Windows, launch J.A.R.V.I.S. On a phone, open the web app and use Add to Home Screen.",
             "Step one. Open the app. On Windows, launch Jarvis. On a phone, open the web app, then Add to Home Screen."),
            ("STEP 2", "Wake Jarvis", "Say “Jarvis Activate”. You can also type in the chat box.",
             "Step two. Say Jarvis Activate. You can also type in the chat box if you do not want to use the microphone."),
            ("STEP 3", "Talk in your language", "Use English, Hindi, or Punjabi. Ask it to open apps, folders, or websites.",
             "Step three. Talk in English, Hindi, or Punjabi. Ask it to open apps, folders, or websites."),
            ("STEP 4", "Privacy stays off", "Microphone and other permissions stay off until you turn them on.",
             "Step four. Privacy stays off until you turn it on. Enable the microphone only when you want voice."),
            ("DONE", "You are ready", "Studio page: sl8722569-ux.github.io/insan-creations/products/jarvis.html",
             "You are ready. Find downloads and this tutorial on the Insan Creations website."),
        ],
    },
    {
        "id": "study-assistant",
        "accent": (212, 160, 23),
        "bg": (16, 22, 48),
        "icon": ICONS / "study-assistant-192.png",
        "hero": FRAMES / "study.jpg",
        "slides": [
            ("INSAN CREATIONS TUTORIAL", "AI Study Assistant", "How to open the study site and use it as an app.",
             "This is a short tutorial for the AI Study Assistant from Insan Creations."),
            ("STEP 1", "Open the website", "Go to the AI Study Assistant page from INSAN CREATIONS or its GitHub site.",
             "Step one. Open the Study Assistant website from Insan Creations, or from its GitHub site."),
            ("STEP 2", "Choose your language", "Pick the language you study in. Mixed-language use is fine.",
             "Step two. Choose the language you study in. You can mix languages if that is how you learn."),
            ("STEP 3", "Ask a study question", "Request an explanation, a plan, or practice on a topic you are learning.",
             "Step three. Ask a study question. Request an explanation, a study plan, or practice on a topic."),
            ("STEP 4", "Install as an app", "In the browser, use Install or Add to Home Screen so it opens like an app.",
             "Step four. In the browser, use Install, or Add to Home Screen, so it opens like an app."),
            ("DONE", "You are ready", "Open: sl8722569-ux.github.io/ai-study-assistant/web/",
             "You are ready. The Study Assistant is on the Insan Creations website."),
        ],
    },
    {
        "id": "univista",
        "accent": (62, 200, 232),
        "bg": (7, 16, 24),
        "icon": ICONS / "univista-192.png",
        "hero": FRAMES / "univista.jpg",
        "slides": [
            ("INSAN CREATIONS TUTORIAL", "UniVista", "Early Access: camera, live view, Mira, and privacy.",
             "This is a short tutorial for UniVista Early Access, the camera and security app from Insan Creations."),
            ("STEP 1", "Open Early Access", "Open the UniVista app from the official site. Install it if you want a home-screen icon.",
             "Step one. Open UniVista Early Access from the official site. You can install it as an app if you want."),
            ("STEP 2", "Allow camera in Privacy", "Open Privacy and enable camera. Also enable snapshots if you want local stills.",
             "Step two. Open Privacy and allow the camera. Enable snapshots only if you want local stills."),
            ("STEP 3", "Start live view", "Go to Live view and tap Start camera. The browser will ask permission.",
             "Step three. Go to Live view and tap Start camera. Your browser will ask permission."),
            ("STEP 4", "Record or ask Mira", "Take a snapshot, record a clip, watch motion, or ask Mira. Files stay on this device.",
             "Step four. Take a snapshot, record a clip, watch motion, or ask Mira. Files stay on this device. Cloud is off."),
            ("DONE", "You are ready", "App: sl8722569-ux.github.io/univista/web/",
             "You are ready. UniVista Early Access is on the Insan Creations website."),
        ],
    },
    {
        "id": "insan-creations",
        "accent": (212, 160, 23),
        "bg": (14, 13, 11),
        "icon": ICONS / "insan-creations-192.png",
        "hero": FRAMES / "studio.jpg",
        "slides": [
            ("STUDIO TUTORIAL", "INSAN CREATIONS", "How to find every app and open the right tutorial.",
             "This is a short tutorial for the Insan Creations studio website."),
            ("STEP 1", "Open the studio site", "Go to the INSAN CREATIONS website. This is the catalogue for every app.",
             "Step one. Open the Insan Creations website. This is the catalogue for every app."),
            ("STEP 2", "Browse all apps", "Use All apps, or the cards on the home page, to see J.A.R.V.I.S, Study Assistant, and UniVista.",
             "Step two. Browse all apps. You will see Jarvis, the Study Assistant, and UniVista."),
            ("STEP 3", "Open a product page", "Each app has downloads or a launch button, plus a tutorial video.",
             "Step three. Open a product page. Each app has a launch or download button, and a tutorial video."),
            ("STEP 4", "Launch or download", "Open the web app, install it, or pick a Windows download for J.A.R.V.I.S.",
             "Step four. Launch the web app, install it on your phone, or download Jarvis for Windows."),
            ("DONE", "You are ready", "Studio: sl8722569-ux.github.io/insan-creations/",
             "You are ready. All apps and tutorials live on the Insan Creations website."),
        ],
    },
    {
        "id": "vaani",
        "accent": (232, 184, 74),
        "bg": (7, 6, 15),
        "icon": ICONS / "language-ai-192.png",
        "hero": FRAMES / "vaani.jpg",
        "slides": [
            ("INSAN CREATIONS TUTORIAL", "Vaani", "Universal language and script AI. How to open, pick a language, learn, and trace.",
             "This is a short tutorial for Vaani, the universal language and script A I from Insan Creations."),
            ("STEP 1", "Open Vaani", "Open Early Access from the INSAN CREATIONS site, or from GitHub Pages. Add to Home Screen if you want an app icon.",
             "Step one. Open Vaani Early Access from the Insan Creations website, or from GitHub Pages. You can add it to your home screen."),
            ("STEP 2", "Pick from the catalogue", "Languages, scripts, varieties and transliteration are separate. Example: Punjabi is a language. Gurmukhi is a script.",
             "Step two. Open the catalogue. Languages, scripts, and transliteration are separate. Punjabi is a language. Gurmukhi is a script."),
            ("STEP 3", "Learn and listen", "Answer meaning, script, reading and listen questions. Tap Hear it. XP and streak stay on this device.",
             "Step three. Use Learn. Answer questions, tap Hear it, and keep your X P and streak on this device."),
            ("STEP 4", "Trace and ask the tutor", "Trace a glyph. Ask the on-device tutor about a greeting or a script. No A I keys are in the page.",
             "Step four. Trace a glyph, or ask the on-device tutor about a greeting or a script. There are no A I keys in the page."),
            ("DONE", "You are ready", "App: sl8722569-ux.github.io/universal-language-ai/web/",
             "You are ready. Vaani is on the Insan Creations website."),
        ],
    },
    {
        "id": "nexcode",
        "accent": (0, 120, 212),
        "bg": (24, 24, 24),
        "icon": ICONS / "nexcode-192.png",
        "hero": FRAMES / "nexcode.jpg",
        "slides": [
            ("INSAN CREATIONS TUTORIAL", "NEXCODE", "Cross-device editor. How to open, edit files, and use Host and Mobile views.",
             "This is a short tutorial for Nexcode, the cross-device editor from Insan Creations."),
            ("STEP 1", "Open NEXCODE", "Open Early Access from the INSAN CREATIONS site or GitHub Pages. Files stay in this browser.",
             "Step one. Open Nexcode Early Access from the Insan Creations website. Files stay in this browser."),
            ("STEP 2", "Open a file", "Use Explorer, or press Control O. Click app.js. Type. It saves on this device.",
             "Step two. Open a file. Use Explorer, or press Control O. Click app.js and type. It saves on this device."),
            ("STEP 3", "Command palette", "Press Control Shift P. Search commands: sessions, mobile view, pairing demo.",
             "Step three. Press Control Shift P for the command palette. Search sessions, mobile view, or pairing."),
            ("STEP 4", "Host and Mobile", "Use the Host and Mobile switch. Same project, smaller chrome. Not a second physical phone yet.",
             "Step four. Switch Host and Mobile. Same project, smaller screen. A real second phone needs a backend later."),
            ("DONE", "You are ready", "App: sl8722569-ux.github.io/nexcode/web/",
             "You are ready. Nexcode is on the Insan Creations website."),
        ],
    },
]


def build_one(spec: dict) -> Path:
    tid = spec["id"]
    work = BUILD / tid
    work.mkdir(parents=True, exist_ok=True)
    clips = []
    wavs = []
    for i, (kicker, title, body, spoken) in enumerate(spec["slides"]):
        png = work / f"s{i:02d}.png"
        card(spec["bg"], spec["accent"], spec["icon"], kicker, title, body, png)
        wav = work / f"s{i:02d}.wav"
        tts(spoken, wav)
        wavs.append(wav)
        dur = probe_dur(wav) + 0.85
        mp4 = work / f"s{i:02d}.mp4"
        still_to_mp4(png, dur, mp4, zoom=False)
        clips.append(mp4)
        if i == 0 and spec["hero"].exists():
            hmp4 = work / "hero.mp4"
            still_to_mp4(spec["hero"], 5.2, hmp4, zoom=True)
            clips.insert(1, hmp4)
            wavs.insert(1, None)

    # build one audio track aligned to clips: concat wavs with silence for hero
    audio_parts = []
    for i, clip in enumerate(clips):
        cd = probe_dur(clip)
        part = work / f"a{i:02d}.wav"
        if i < len(wavs) and wavs[i] is not None:
            # pad wav to clip length
            subprocess.check_call(
                [
                    str(FFMPEG), "-y", "-i", str(wavs[i]),
                    "-af", f"apad=pad_dur={cd}", "-t", f"{cd:.2f}",
                    str(part),
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        else:
            ref = next(w for w in wavs if w is not None)
            subprocess.check_call(
                [
                    str(FFMPEG), "-y", "-i", str(ref), "-t", f"{cd:.2f}",
                    "-af", "volume=0", str(part),
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        audio_parts.append(part)

    alist = work / "audio.txt"
    alist.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_parts), encoding="utf-8")
    audio = work / "narration.wav"
    subprocess.check_call(
        [str(FFMPEG), "-y", "-f", "concat", "-safe", "0", "-i", str(alist), "-c:a", "pcm_s16le", str(audio)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    out = ROOT / f"tutorial-{tid}.mp4"
    concat(clips, audio, out)
    print("built", out, "size", out.stat().st_size)
    return out


def main() -> int:
    if not FFMPEG.exists():
        print("ffmpeg missing", FFMPEG, file=sys.stderr)
        return 1
    BUILD.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for spec in TUTORIALS:
        if only and spec["id"] != only:
            continue
        build_one(spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
