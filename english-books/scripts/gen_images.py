"""Generate illustrations for every unit with a Gemini image model.

Usage: python3 scripts/gen_images.py [grade ...]
Already generated images are skipped, so the script can be re-run any time.
Needs a GEMINI_API_KEY with image quota (paid tier); stops cleanly when quota runs out.
"""
import base64
import io
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

from topics import BOOKS

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("IMAGE_MODEL", "gemini-3.1-flash-image")
KEY = os.environ["GEMINI_API_KEY"]

STYLE = ("Vibrant children's picture-book illustration, warm hand-painted digital style, bold friendly "
         "shapes, rich cheerful colors, soft lighting, cute expressive characters, high detail that "
         "invites kids to look closer. Absolutely no text, letters, numbers or words in the image.")
STICKER = ("Cute die-cut sticker illustration for a kids' vocabulary flashcard, single subject centered, "
           "bold clean outline, bright cheerful colors, soft shading, plain white background. "
           "Absolutely no text, letters or words.")

stop = threading.Event()


def jobs_for(grade):
    """(output path, prompt, aspect ratio, max width) for every picture the book uses."""
    book = BOOKS[grade]
    out = [(ROOT / f"images/grade{grade}/cover.jpg",
            f"{STYLE} Book cover art for an English book for Vietnamese Grade {grade} kids: happy children "
            f"on a colorful adventure with books, stars, a rainbow and friendly animals, room at the top "
            f"for a title.", "3:4", 1400)]
    for f in sorted((ROOT / f"content/grade{grade}").glob("unit*.json")):
        u = json.loads(f.read_text())
        d = ROOT / f"images/grade{grade}/{f.stem}"
        out.append((d / "cover.jpg", f"{STYLE} Wide scene: {u['cover_image_prompt']}", "16:9", 1600))
        for i, v in enumerate(u["vocabulary"]):
            out.append((d / f"vocab{i:02d}.jpg", f"{STICKER} Subject: {v['en']} – {v['image_prompt']}",
                        "1:1", 512))
        for i, r in enumerate(u["readings"]):
            out.append((d / f"reading{i}.jpg", f"{STYLE} {r['image_prompt']}", "4:3", 1100))
        panels = " ".join(f"Panel {i + 1}: {p['scene']}" for i, p in enumerate(u["comic"]["panels"]))
        out.append((d / "comic.jpg", f"{STYLE} A 4-panel comic strip in a 2x2 grid with white gutters, "
                    f"same characters in every panel, no speech bubbles. {panels}", "1:1", 1400))
        for i, c in enumerate(u["conversations"]):
            out.append((d / f"conv{i}.jpg", f"{STYLE} {c['image_prompt']}", "4:3", 1000))
        out.append((d / "value.jpg", f"{STYLE} {u['life_skill']['image_prompt']}", "4:3", 1000))
        out.append((d / "project.jpg", f"{STYLE} {u['project']['image_prompt']}", "4:3", 1000))
    return out


def generate(path, prompt, ratio, width):
    if path.exists() or stop.is_set():
        return None
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ratio}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=300))
            data = next(p["inlineData"]["data"] for p in d["candidates"][0]["content"]["parts"]
                        if "inlineData" in p)
            im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            path.parent.mkdir(parents=True, exist_ok=True)
            im.save(path, "JPEG", quality=84, optimize=True)
            return f"ok {path.relative_to(ROOT)}"
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            if e.code == 429 and ("limit: 0" in msg or "per day" in msg):
                stop.set()
                return "QUOTA: this API key has no image quota left (enable billing in Google AI Studio)."
            time.sleep(15 * (attempt + 1))
        except (StopIteration, KeyError, OSError):
            time.sleep(5)
    return f"failed {path.relative_to(ROOT)}"


if __name__ == "__main__":
    grades = [int(g) for g in sys.argv[1:]] or list(BOOKS)
    jobs = [j for g in grades for j in jobs_for(g)]
    print(f"{sum(not j[0].exists() for j in jobs)} of {len(jobs)} images to generate")
    with ThreadPoolExecutor(int(os.environ.get("WORKERS", 6))) as ex:
        for r in ex.map(lambda j: generate(*j), jobs):
            if r:
                print(r, flush=True)
