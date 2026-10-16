"""Record the one narrated, captioned demo for Projects 4 and 5 (production hardening + client handoff).

python scripts/record_demo.py --web-out ../vamsi-portfolio/videos/production-and-handoff-demo.mp4 \
    --linkedin-out ../linkedin-post-4/video.mp4

Scenes, all real:
1. The LIVE assistant: a Spanish question answered in Spanish with a source; an emergency answered at once.
2. The LIVE agent: E12, a Mountain Lodge guest writing to the Beach Resort inbox, answered for the right hotel.
3. The owner's Operations page on a LOCAL run of the same assistant code (SQLite log, one-time password generated
   here and never printed or shown; the live Admin password is never typed), after asking two questions there.
4. This handoff package on GitHub: the runbooks.

Narration: Piper en_US-lessac-high (open source, offline), labelled "Narration: AI voice". Captions: a WebVTT track
and a burned-in copy for LinkedIn. Costs a few API calls (two questions on the local run; the live runs may reuse
results). Dev-only: Playwright, piper-tts, Pillow and ffmpeg on PATH. docs/video/ is git-ignored.
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
P1 = ROOT.parent / "hotel-ops-assistant"
OUT = ROOT / "docs" / "video"
WORK = OUT / "work"
VOICES = OUT / "voices"
SHARED_VOICES = ROOT.parent / "guest-request-agent" / "docs" / "video" / "voices"
VOICE = "en_US-lessac-high"
P1_APP = "https://hotel-ops-assistant.streamlit.app/~/+/"
P2_APP = "https://guest-request-agent.streamlit.app/~/+/"
HANDOFF = "https://github.com/vamsialladev/hotel-ai-handoff/blob/main/docs/RUNBOOKS.md"
LOCAL_PORT = 8540
SIZE = (1280, 720)
VIEW = (1280, 640)
FPS = 30
MSG = "[data-testid=stChatMessage]"
GREEN, BRASS, CREAM, INK = "#1E4636", "#94702C", "#F4F1EA", "#FFFFFF"
LINKS = [
    ("Case study", "vamsialla.com/projects/production-and-handoff.html"),
    ("Handoff package", "github.com/vamsialladev/hotel-ai-handoff"),
    ("Live apps", "hotel-ops-assistant.streamlit.app · guest-request-agent.streamlit.app"),
]
TITLE = "Production and handoff"
SUBTITLE = "Simulated client engagement · synthetic data · parts four and five of five"
TITLE_SECONDS = 3
LEAD, GAP = 0.4, 0.35
SPEED = 1.08

NARRATION = {
    "title": "Production and handoff: a simulated client project, parts four and five of five.",
    "spanish": "The eval harness found real gaps. Spanish questions were blocked before they reached the model. "
    "Now the answer comes back in Spanish, from the English documents, with its source.",
    "safety": "Emergencies in other words, or in Spanish, were missed. Now they get the safety message at once, "
    "with no model call.",
    "agent": "A guest booked at the Mountain Lodge wrote to the Beach Resort. The agent used to answer for the wrong "
    "hotel. Now the booking is looked up first, so the reply is about the right one.",
    "ops": "On a local copy, the owner's Operations page shows requests, latency and cost against budgets. Every "
    "log record has personal data removed before it is stored, and is kept for thirty days.",
    "handoff": "And the handoff package: runbooks, service levels, staff guides, and a daily health check that "
    "knows a sleeping free app from a broken one.",
    "end": "Every number comes from a saved run. The links are on screen.",
}
CAPTIONS = {
    "spanish": "Spanish question → Spanish answer, cited (was blocked before the model).",
    "safety": "Emergency in other words → safety message at once, no model call.",
    "agent": "Wrong inbox (E12) → booking looked up first → the right hotel's policy.",
    "ops": "Operations page (local run, test password): budgets, cost, latency.",
    "handoff": "Handoff package: runbooks, SLOs, guides, daily health check.",
}


# ---------------------------------------------------------------- narration
def voice_model() -> Path:
    model = VOICES / f"{VOICE}.onnx"
    if not model.exists():
        VOICES.mkdir(parents=True, exist_ok=True)
        shared = SHARED_VOICES / f"{VOICE}.onnx"
        if shared.exists():
            for f in SHARED_VOICES.glob(f"{VOICE}.onnx*"):
                shutil.copy(f, VOICES / f.name)
        else:
            subprocess.run(
                [sys.executable, "-m", "piper.download_voices", VOICE, "--download-dir", str(VOICES)], check=True
            )
    return model


def wav_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def synthesize(lines: dict, folder: Path) -> dict:
    from piper import PiperVoice, SynthesisConfig

    voice = PiperVoice.load(str(voice_model()))
    config = SynthesisConfig(length_scale=SPEED)
    folder.mkdir(parents=True, exist_ok=True)
    durations = {}
    for key, text in lines.items():
        path = folder / f"{key}.wav"
        with wave.open(str(path), "wb") as w:
            voice.synthesize_wav(text, w, syn_config=config)
        durations[key] = round(wav_seconds(path), 2)
    return durations


# ---------------------------------------------------------------- recording
class Recorder:
    def __init__(self, page, durations: dict):
        self.page, self.t0, self.steps, self.durations = page, time.monotonic(), [], durations
        self.trim = None
        self.cursor = LEAD + durations.get("title", 0) + GAP

    def now(self) -> float:
        return round(time.monotonic() - self.t0, 2)

    def video_time(self) -> float:
        return self.now() - self.trim + TITLE_SECONDS

    def step(self, key: str):
        start = self.video_time()
        audio = max(start + LEAD, self.cursor)
        self.cursor = audio + self.durations.get(key, 0) + GAP
        self.steps.append({"key": key, "caption": CAPTIONS[key], "start": self.now(), "audio": round(audio, 2)})

    def settle(self, at_least: float):
        self.pause(at_least)
        while self.video_time() < self.cursor - GAP:
            self.page.wait_for_timeout(100)

    def pause(self, seconds: float):
        self.page.wait_for_timeout(int(seconds * 1000))

    def scroll(self, pixels: int, steps: int = 12):
        self.page.mouse.move(800, 400)
        for _ in range(steps):
            self.page.mouse.wheel(0, pixels / steps)
            self.page.wait_for_timeout(45)


def ready_p1(page):
    page.wait_for_selector("h1.hoa-title", timeout=240_000)
    page.wait_for_timeout(2000)


def ready_p2(page):
    page.wait_for_selector("h1.gra-title", timeout=240_000)
    page.wait_for_timeout(1500)


def to_bottom(page):
    page.mouse.move(800, 300)
    for _ in range(10):
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(30)


def ask(page, text: str):
    """Type a question like a person and wait until the whole reply (with its status line) is on screen."""
    before = page.locator(MSG).count()
    to_bottom(page)
    box = page.locator("[data-testid=stChatInputTextArea]")
    box.click()
    box.press_sequentially(text, delay=40)
    page.wait_for_timeout(300)
    box.press("Enter")
    page.wait_for_function(f"document.querySelectorAll('{MSG}').length >= {before + 2}", timeout=120_000)
    answer = page.locator(MSG).nth(before + 1)
    answer.locator(".hoa-status, [data-testid=stButton], [data-testid=stAlert]").first.wait_for(timeout=120_000)
    page.wait_for_timeout(500)
    answer.evaluate("el => el.scrollIntoView({block: 'end', behavior: 'smooth'})")
    page.wait_for_timeout(700)
    return answer


def show(page, text: str):
    page.get_by_text(text, exact=False).locator("visible=true").first.evaluate(
        "el => el.scrollIntoView({block: 'start', behavior: 'smooth'})"
    )
    page.wait_for_timeout(900)


def wake(browser, url: str, ready):
    """Not recorded: open the app once so a sleeping free app is awake before recording starts."""
    p = browser.new_page()
    p.goto(url, timeout=240_000)
    try:
        p.get_by_role("button", name=re.compile("get this app back up", re.I)).click(timeout=8_000)
    except Exception:  # noqa: BLE001 - awake already
        pass
    ready(p)
    p.close()


def start_local(password: str, log_dir: str) -> subprocess.Popen:
    """A local run of the assistant for the Operations segment: its own SQLite log and a one-time password."""
    env = {
        **os.environ,
        "ADMIN_PASSWORD": password,
        "LOG_DIR": log_dir,
        "DATABASE_URL": f"sqlite:///{Path(log_dir, 'logs.db').as_posix()}",
        "USE_EMBEDDINGS": "false",
        "PRICE_IN_PER_M": "0.10",
        "PRICE_OUT_PER_M": "0.50",
    }
    env.pop("STAFF_PASSWORD", None)
    # A clean export of the committed code: no .streamlit/secrets.toml (Streamlit would let it override the one-time
    # password) and no .env. Only the API key is passed, in memory, for the two preparation questions.
    from dotenv import dotenv_values

    env["ANTHROPIC_API_KEY"] = dotenv_values(P1 / ".env").get("ANTHROPIC_API_KEY") or ""
    tree = Path(log_dir) / "app"
    tree.mkdir()
    archive = subprocess.run(["git", "-C", str(P1), "archive", "HEAD"], check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
    python = P1 / ".venv" / "Scripts" / "python.exe"
    subprocess.run(
        [str(python), "-m", "src.ingest", "--bm25-only"],
        cwd=tree,
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    cmd = [
        str(python),
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        str(LOCAL_PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    proc = subprocess.Popen(cmd, cwd=tree, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import urllib.request

    for _ in range(90):
        try:
            urllib.request.urlopen(f"http://localhost:{LOCAL_PORT}/_stcore/health", timeout=2)
            return proc
        except OSError:
            time.sleep(1)
    proc.terminate()
    raise SystemExit("The local app didn't start.")


def record(durations: dict) -> dict:
    from playwright.sync_api import sync_playwright

    local = f"http://localhost:{LOCAL_PORT}/"
    password = secrets.token_urlsafe(24)
    logs = tempfile.mkdtemp(prefix="p4-demo-logs-")
    proc = start_local(password, logs)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            wake(browser, P1_APP, ready_p1)
            wake(browser, P2_APP, ready_p2)
            prep = browser.new_page()  # not recorded: two real questions on the local run, for the Operations page
            prep.goto(local, timeout=120_000)
            ready_p1(prep)
            ask(prep, "¿Cuánto cuesta el estacionamiento?")
            ask(prep, "My name is Priya Shah, call me at (555) 123-4567: is there a pet fee?")
            prep.close()

            ctx = browser.new_context(
                viewport={"width": VIEW[0], "height": VIEW[1]},
                record_video_dir=str(WORK),
                record_video_size={"width": VIEW[0], "height": VIEW[1]},
                color_scheme="light",
            )
            page = ctx.new_page()
            r = Recorder(page, durations)
            page.goto(P1_APP, timeout=240_000)
            ready_p1(page)
            r.trim = r.now()

            r.step("spanish")
            ask(page, "¿Cuánto cuesta el estacionamiento?")
            r.settle(2)

            r.step("safety")
            ask(page, "There's smoke coming from under a guest room door. What should I do?")
            r.settle(2)

            r.step("agent")
            page.goto(f"{P2_APP}?email=E12", timeout=240_000)
            ready_p2(page)
            show(page, "Pool hours for the kids")
            button = page.locator("button", has_text=re.compile("Run the agent on this email|Show the agent's result"))
            button.first.wait_for(timeout=180_000)
            r.pause(1.2)
            button.first.click()
            page.get_by_text("Draft reply", exact=False).first.wait_for(timeout=180_000)
            show(page, "Draft reply")
            r.settle(2.5)

            r.step("ops")
            page.goto(f"{local}admin", timeout=120_000)
            ready_p1(page)
            page.locator("input[type=password]").first.fill(password)
            page.get_by_role("button", name="Unlock").click()
            page.wait_for_selector("h1.hoa-title:has-text('Admin')", timeout=60_000)
            page.locator("[data-testid=stSidebarNav] a", has_text="Operations").first.click()  # same session
            page.wait_for_selector("h1.hoa-title:has-text('Operations')", timeout=60_000)
            r.pause(2)
            show(page, "Budgets")
            r.pause(1.5)
            show(page, "System")
            r.settle(1.5)

            r.step("handoff")
            page.goto(HANDOFF, timeout=120_000)
            page.wait_for_timeout(2500)
            r.scroll(500, 16)
            r.settle(1.5)
            end = r.now()

            video = page.video
            ctx.close()
            raw = Path(video.path())
            browser.close()
        raw.rename(WORK / "raw.webm")
    finally:
        proc.terminate()
        shutil.rmtree(logs, ignore_errors=True)
    timeline = {"trim": r.trim, "end": end, "steps": r.steps, "durations": durations, "end_audio": None}
    (WORK / "timeline.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    return timeline


# ---------------------------------------------------------------- building (same pipeline as Projects 1-3)
def font(name: str, size: int):
    for candidate in (name, "arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def centered(draw, y, text, fnt, fill):
    width = draw.textlength(text, font=fnt)
    draw.text(((SIZE[0] - width) / 2, y), text, font=fnt, fill=fill)


def title_card(path: Path):
    img = Image.new("RGB", SIZE, GREEN)
    d = ImageDraw.Draw(img)
    d.rectangle([0, SIZE[1] - 14, SIZE[0], SIZE[1]], fill=BRASS)
    centered(d, 250, TITLE, font("georgiab.ttf", 58), INK)
    centered(d, 340, "Vamsi Alla", font("georgia.ttf", 38), "#E8D9B5")
    centered(d, 430, SUBTITLE, font("arial.ttf", 24), CREAM)
    img.save(path)


def end_card(path: Path, narrated: bool = True):
    img = Image.new("RGB", SIZE, GREEN)
    d = ImageDraw.Draw(img)
    d.rectangle([0, SIZE[1] - 14, SIZE[0], SIZE[1]], fill=BRASS)
    centered(d, 140, "The case study, the handoff package and the apps", font("georgiab.ttf", 40), INK)
    label_font, link_font = font("arialbd.ttf", 24), font("arial.ttf", 28)
    for i, (label, url) in enumerate(LINKS):
        y = 250 + i * 90
        centered(d, y, label.upper(), label_font, "#E8D9B5")
        centered(d, y + 32, url, link_font, INK)
    if narrated:
        centered(d, 600, "Narration: AI voice (Piper, open source)", font("arial.ttf", 22), CREAM)
    img.save(path)


def ass_time(seconds: float) -> str:
    seconds = max(seconds, 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def vtt_time(seconds: float) -> str:
    seconds = max(seconds, 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def captions(timeline: dict, offset: float) -> str:
    head = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Cap,Arial,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,2,40,40,24,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    steps, lines = timeline["steps"], []
    for i, step in enumerate(steps):
        start = step["start"] - timeline["trim"] + offset
        stop = (steps[i + 1]["start"] if i + 1 < len(steps) else timeline["end"]) - timeline["trim"] + offset
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(stop - 0.05)},Cap,,0,0,0,,{step['caption']}")
    return head + "\n".join(lines) + "\n"


def narration_cues(timeline: dict) -> list[tuple[float, float, str]]:
    durations = timeline["durations"]
    lines = [(LEAD, "title")] + [(s["audio"], s["key"]) for s in timeline["steps"]]
    if timeline.get("end_audio") is not None:
        lines.append((timeline["end_audio"], "end"))
    cues = []
    for start, key in lines:
        text, length = NARRATION[key], durations.get(key, 0)
        sentences = [s for s in re.split(r"(?<=[.:?!])\s+(?=[A-Z])", text) if s]
        total, t = sum(len(s) for s in sentences), start
        for s in sentences:
            span = length * len(s) / total
            cues.append((round(t, 2), round(t + span, 2), s))
            t += span
    return cues


VTT_POSITION = "line:6% position:50% align:center"


def webvtt(cues) -> str:
    return "WEBVTT\n\n" + "\n".join(f"{vtt_time(a)} --> {vtt_time(b)} {VTT_POSITION}\n{text}\n" for a, b, text in cues)


def ffmpeg(*args: str):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True, cwd=WORK)


def mix_narration(timeline: dict, total: float) -> Path:
    clips = [("title", LEAD)] + [(s["key"], s["audio"]) for s in timeline["steps"]] + [("end", timeline["end_audio"])]
    inputs, chains = [], []
    for i, (key, at) in enumerate(clips):
        inputs += ["-i", f"voice/{key}.wav"]
        ms = int(at * 1000)
        chains.append(f"[{i}:a]adelay={ms}|{ms},aresample=48000[a{i}]")
    graph = ";".join(chains) + ";" + "".join(f"[a{i}]" for i in range(len(clips)))
    graph += f"amix=inputs={len(clips)}:normalize=0,apad=whole_dur={total:.2f},loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    ffmpeg(
        *inputs,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-t",
        f"{total:.2f}",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "narration.m4a",
    )
    return WORK / "narration.m4a"


def build(timeline: dict, voice: bool) -> Path:
    length = timeline["end"] - timeline["trim"]
    durations = timeline["durations"]
    end_audio = TITLE_SECONDS + length + LEAD if voice else None
    end_seconds = max(6.0, (durations.get("end", 0) + LEAD + 1.2) if voice else 6.0)
    timeline["end_audio"] = end_audio
    total = TITLE_SECONDS + length + end_seconds
    title_card(WORK / "title.png")
    end_card(WORK / "end.png", narrated=voice)
    (WORK / "captions.ass").write_text(captions(timeline, TITLE_SECONDS), encoding="utf-8")
    scale = f"scale={SIZE[0]}:{SIZE[1]},fps={FPS},format=yuv420p,setsar=1"
    band = f"scale={VIEW[0]}:{VIEW[1]},pad={SIZE[0]}:{SIZE[1]}:0:0:color=0x111111,fps={FPS},format=yuv420p,setsar=1"
    graph = (
        f"[0:v]{scale},fade=t=out:st={TITLE_SECONDS - 0.4}:d=0.4[t];"
        f"[1:v]{band},fade=t=in:st=0:d=0.4[m];"
        f"[2:v]{scale},fade=t=in:st=0:d=0.4[e];"
        "[t][m][e]concat=n=3:v=1:a=0,subtitles=captions.ass[v]"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "demo.mp4"
    audio = ["-i", str(mix_narration(timeline, total)), "-map", "3:a", "-c:a", "copy"] if voice else []
    ffmpeg(
        *("-loop", "1", "-t", str(TITLE_SECONDS), "-i", "title.png"),
        *("-ss", f"{timeline['trim']:.2f}", "-t", f"{length:.2f}", "-i", "raw.webm"),
        *("-loop", "1", "-t", f"{end_seconds:.2f}", "-i", "end.png"),
        *audio[:2],
        *("-filter_complex", graph, "-map", "[v]"),
        *audio[2:],
        *("-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart"),
        *("-t", f"{total:.2f}"),
        str(out),
    )
    if voice:
        cues = narration_cues(timeline)
        (OUT / "demo.vtt").write_text(webvtt(cues), encoding="utf-8")
        lines = [f"[{int(a // 60)}:{a % 60:04.1f}] {text}" for a, _, text in cues]
        (OUT / "narration-script.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (WORK / "timeline.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    return out


def web_copy(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(
        *("-i", str(src), "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-profile:v", "high"),
        *("-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)),
    )
    ffmpeg("-ss", "1.5", "-i", str(src), "-frames:v", "1", "-q:v", "3", str(dest.with_name(dest.stem + "-poster.jpg")))
    if (OUT / "demo.vtt").exists():
        shutil.copy(OUT / "demo.vtt", dest.with_suffix(".vtt"))


def linkedin_copy(dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    cues = narration_cues(json.loads((WORK / "timeline.json").read_text(encoding="utf-8")))
    srt = "".join(
        f"{i}\n{vtt_time(a).replace('.', ',')} --> {vtt_time(b).replace('.', ',')}\n{text}\n\n"
        for i, (a, b, text) in enumerate(cues, 1)
    )
    (OUT / "demo.srt").write_text(srt, encoding="utf-8")
    style = (
        "FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=4,Alignment=6,MarginV=14"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            "demo.mp4",
            "-vf",
            f"subtitles=demo.srt:force_style='{style}'",
            "-c:v",
            "libx264",
            "-crf",
            "22",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(dest),
        ],
        check=True,
        cwd=OUT,
    )
    card = Image.open(WORK / "title.png").convert("RGB")
    width = round(card.height * 1200 / 627)
    left = (card.width - width) // 2
    card.crop((left, 0, left + width, card.height)).resize((1200, 627)).save(
        dest.with_name("thumbnail.jpg"), quality=88
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rebuild", action="store_true", help="reuse the last recording and narration")
    parser.add_argument("--web-out", type=Path)
    parser.add_argument("--linkedin-out", type=Path)
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found (winget install Gyan.FFmpeg).")
    if args.rebuild:
        timeline = json.loads((WORK / "timeline.json").read_text(encoding="utf-8"))
    else:
        shutil.rmtree(WORK, ignore_errors=True)
        WORK.mkdir(parents=True)
        timeline = record(synthesize(NARRATION, WORK / "voice"))
    out = build(timeline, True)
    print(f"saved {out.relative_to(ROOT)}")
    if args.web_out:
        web_copy(out, args.web_out.resolve())
        print(f"saved {args.web_out} (+ poster .jpg and .vtt)")
    if args.linkedin_out:
        linkedin_copy(args.linkedin_out.resolve())
        print(f"saved {args.linkedin_out} and thumbnail.jpg")


if __name__ == "__main__":
    main()
