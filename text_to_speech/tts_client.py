import asyncio, io, math, os, re, struct, tempfile, wave
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
VOICES = {"Default": "YTpq7expH9539ERJ"}  # add more from Gradium's voice library later


def get_backend():
    """Which speech source to use: 'mock', 'phonon' or 'gradium'."""
    default = "gradium" if os.getenv("GRADIUM_API_KEY") else "mock"
    return (os.getenv("TTS_BACKEND") or default).lower()


# ---------- backend 1: mock (placeholder beep, no setup needed) ----------
def _mock_wav(text):
    rate = 24000
    seconds = min(max(len(text) * 0.05, 0.5), 20)
    frames = b"".join(
        struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / rate)))
        for i in range(int(rate * seconds))
    )
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(frames)
    return buf.getvalue()


# ---------- backend 2: Phonon (local model, optional: pip install ptts) ----------
@lru_cache(maxsize=1)
def _phonon_model():
    import ptts  # imported here so the app still runs without it installed
    return ptts.TTS(lang="en")


def _phonon_wav(text):
    tts = _phonon_model()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "out.wav"
        tts.save(str(path), text)
        return path.read_bytes()


# ---------- backend 3: Gradium hosted API ----------
async def _gradium_call(text, voice_id, speed):
    import gradium
    client = gradium.client.GradiumClient()
    result = await client.tts(
        setup={"voice_id": voice_id, "output_format": "wav",
               "json_config": {"padding_bonus": speed}},
        text=text,
    )
    return result.raw_data


# ---------- shared helpers ----------
def split_chunks(text, limit=400):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, current = [], ""
    for s in sentences:
        if current and len(current) + len(s) > limit:
            chunks.append(current); current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current)
    return chunks


def _join_wavs(parts):
    with wave.open(io.BytesIO(parts[0])) as w0:
        params = w0.getparams()
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        for p in parts:
            with wave.open(io.BytesIO(p)) as r:
                w.writeframes(r.readframes(r.getnframes()))
    return out.getvalue()


def synthesize(text, voice_id=VOICES["Default"], speed=0.0):
    """Returns (wav_bytes, backend_name). Splits long text into chunks."""
    backend = get_backend()
    parts = []
    for chunk in split_chunks(text):
        if backend == "gradium":
            parts.append(asyncio.run(_gradium_call(chunk, voice_id, speed)))
        elif backend == "phonon":
            parts.append(_phonon_wav(chunk))
        else:
            parts.append(_mock_wav(chunk))
    return _join_wavs(parts), backend