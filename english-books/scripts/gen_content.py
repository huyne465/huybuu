"""Draft every unit's content with Gemini (text model) and save it as JSON.

Usage: python3 scripts/gen_content.py [grade ...]   (skips units already in content/)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from topics import BOOKS

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("TEXT_MODEL", "gemini-2.5-flash")
KEY = os.environ["GEMINI_API_KEY"]
STYLE = (ROOT / "reference" / "sample_style.md").read_text()

SCHEMA = """{
 "title": "MY SCHOOL", "theme": "School Life",
 "goal": "Students can ... (one sentence)",
 "goal_vi": "Học sinh có thể ... (Vietnamese)",
 "cover_emoji": "🏫🎒📚",
 "cover_image_prompt": "wide scene that sums up the unit",
 "big_question": {"en": "...?", "vi": "...?", "prompts": ["6 short warm-up questions"]},
 "vocabulary": [{"en": "school", "ipa": "/skuːl/", "vi": "trường học", "emoji": "🏫",
                 "image_prompt": "a single object/action, described so it can be drawn alone"}],
 "phonics": {"sound": "/s/", "letters": "s", "words": ["6 words with the sound, prefer unit words"],
             "chant": "2-line tongue twister using the sound", "tip_vi": "mẹo phát âm ngắn"},
 "patterns": [{"pattern": "There is a/an + noun.", "vi": "nghĩa", "examples": ["3 examples"]}],
 "grammar": [{"title": "There is / There are", "explain_en": "1-2 simple sentences",
              "explain_vi": "giải thích tiếng Việt", "examples": ["3-4 examples"],
              "right": "✅ sentence", "wrong": "❌ common mistake"}],
 "song": {"title": "...", "tune": "Sing to the tune of 'Twinkle Twinkle Little Star' (or another famous kids tune)",
          "lines": ["8-12 short singable lines"], "actions_vi": "gợi ý động tác khi hát"},
 "readings": [{"level": "EASY", "title": "MY SCHOOL", "text": "...", "image_prompt": "...",
               "vocab": [{"en": "", "ipa": "", "vi": ""}], "questions": ["10 questions"],
               "true_false": [{"statement": "...", "answer": true}]}],
 "comic": {"title": "...", "panels": [{"scene": "what we see (for the illustrator)", "speech": "Character: line"}]},
 "speak_up": {"questions": ["15 questions"], "model": "speaking model paragraph",
              "challenge": "Talk about ... for 30–60 seconds."},
 "conversations": [{"title": "At School", "image_prompt": "...", "lines": [{"speaker": "Anna", "text": "..."}]}],
 "listening": {"script": "teacher's script", "questions": ["10 questions"]},
 "brain_games": {"word_search": ["8 single unit words, letters only, max 9 letters"],
                 "odd_one_out": [{"options": ["4 words"], "answer": "the odd word", "why_vi": "lý do"}],
                 "riddles": [{"riddle": "I am ... What am I?", "answer": "..."}],
                 "scramble": [{"scrambled": "oclohs", "answer": "school"}],
                 "picture_count": {"question": "How many ... can you see? (about the cover picture)", "hint_vi": "..."}},
 "write": {"profile_title": "My School Profile", "profile_fields": ["My name is:", "..."],
           "frame_title": "MY SCHOOL", "frame_lines": ["My name is ____.", "..."]},
 "life_skill": {"title": "LOVE AND RESPECT YOUR SCHOOL", "intro": "...", "intro_vi": "...",
                "can_do": ["12 short good habits"], "value_question": "...?", "image_prompt": "..."},
 "fun_facts": [{"en": "Did you know? ... (true, kid-friendly)", "vi": "..."}],
 "project": {"title": "MY DREAM SCHOOL POSTER", "task": "Create a poster about ...",
             "draw_items": ["8 things to draw"], "example": ["5-8 example sentences"],
             "present": "Hello everyone! This is ...", "image_prompt": "..."},
 "classroom_game": {"name": "...", "players": "pairs / groups of 4 / whole class",
                    "steps_en": ["4-5 steps"], "steps_vi": ["same steps in Vietnamese"], "language": ["target sentences used"]},
 "review": {"complete_words": [{"word": "sch__l", "answer": "school"}],
            "mcq": [{"q": "This ______ my school.", "options": ["am", "is", "are"], "answer": "is"}],
            "order": [{"words": "is / This / school / my", "answer": "This is my school."}],
            "about_you": ["10 personal questions"]},
 "i_can": ["15 statements starting with 'I can'"],
 "message_en": "SCHOOL IS A PLACE TO LEARN, TO LOVE, AND TO GROW.",
 "message_vi": "...", "message_body": "2-3 sentence warm closing paragraph",
 "value_line": "Learn English – Learn to Love – Learn to Grow."
}"""

COUNTS = {
    "vocabulary": 20, "patterns": 8, "grammar": 4, "readings": 3, "conversations": 2,
    "fun_facts": 5, "i_can": 15,
}


def prompt_for(grade, title, theme, prev_titles):
    book = BOOKS[grade]
    w1, w2, w3 = book["reading_words"]
    return f"""You are an expert ESL author writing ROXY ENGLISH, a coursebook for Vietnamese primary pupils.
Write ONE complete unit as JSON for: Grade {grade} ({book['level']}), unit "{title}", theme "{theme}".
Learner profile: {book['notes']}
Other units in this book (avoid repeating their vocabulary): {', '.join(prev_titles)}.

Follow the voice and section style of this sample unit (it is the house style; expand on it, do not copy it):
---
{STYLE}
---

Return ONLY JSON matching this shape exactly (all keys required; the sample values only show format):
{SCHEMA}

Hard requirements:
- vocabulary: exactly 20 items, all concrete/drawable where possible; IPA in American English; accurate Vietnamese; one fitting emoji each.
- patterns: exactly 8. grammar: exactly 4.
- readings: exactly 3 with levels "EASY", "MORE PRACTICE", "CHALLENGE" and about {w1}, {w2}, {w3} words; each with exactly 10 vocab rows, 10 questions, 5 true_false items.
- comic: exactly 4 panels telling a tiny funny story with the unit language. speech format "Name: line".
- speak_up: 15 questions. conversations: exactly 2, each 8-10 lines between two named children.
- listening script about {w2} words with 10 questions.
- brain_games: word_search 8 words; odd_one_out 5; riddles 3; scramble 6.
- write: 10 profile_fields and 10 frame_lines (use ____ for blanks).
- life_skill: 12 can_do. fun_facts: exactly 5, factually true. project: 8 draw_items.
- review: complete_words 10, mcq 10 (3 options, answer is one of them), order 10, about_you 10.
- i_can: exactly 15.
- Every image_prompt describes a cheerful scene for a children's book illustrator, with Vietnamese or diverse kids where people appear, and must not ask for any text or letters in the image.
- Names: mix Vietnamese names (Nam, Mai, Linh, Minh, An...) and English names (Ben, Mia, Tom, Lucy...).
- Language must be natural, correct, and right for the grade level. Vietnamese must have full diacritics.
"""


def call(prompt):
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.8,
                             "maxOutputTokens": 60000},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    parts = d["candidates"][0]["content"]["parts"]
    return json.loads("".join(p.get("text", "") for p in parts if not p.get("thought")))


def validate(u):
    errs = [f"{k}: {len(u.get(k, []))}!={n}" for k, n in COUNTS.items() if len(u.get(k, [])) != n]
    for r in u.get("readings", []):
        for k, n in (("vocab", 10), ("questions", 10), ("true_false", 5)):
            if len(r.get(k, [])) != n:
                errs.append(f"reading {r.get('level')} {k}")
    if len(u.get("comic", {}).get("panels", [])) != 4:
        errs.append("comic panels")
    rv = u.get("review", {})
    for k in ("complete_words", "mcq", "order", "about_you"):
        if len(rv.get(k, [])) != 10:
            errs.append(f"review {k}")
    for m in rv.get("mcq", []):
        if m.get("answer") not in m.get("options", []):
            errs.append(f"mcq answer {m.get('q')}")
    if len(u.get("brain_games", {}).get("word_search", [])) != 8:
        errs.append("word_search")
    return errs


def make(grade, idx, title, theme, titles):
    out = ROOT / "content" / f"grade{grade}" / f"unit{idx:02d}.json"
    if out.exists():
        return f"skip {out.name}"
    out.parent.mkdir(parents=True, exist_ok=True)
    prompt = prompt_for(grade, title, theme, [t for t in titles if t != title])
    errs = []
    for attempt in range(5):
        try:
            u = call(prompt)
        except urllib.error.HTTPError as e:
            errs = [f"HTTP {e.code}"]
            time.sleep(30 * (attempt + 1))
            continue
        except Exception as e:  # malformed JSON, timeouts
            errs = [repr(e)[:120]]
            continue
        errs = validate(u)
        if len(errs) <= 2:  # tiny count slips are fixed by hand during review
            u["unit"], u["grade"] = idx, grade
            u["validation"] = errs
            out.write_text(json.dumps(u, ensure_ascii=False, indent=1))
            return f"G{grade} U{idx} ok {errs}"
    return f"G{grade} U{idx} FAILED {errs}"


if __name__ == "__main__":
    grades = [int(g) for g in sys.argv[1:]] or list(BOOKS)
    jobs = []
    for g in grades:
        titles = [t for t, _ in BOOKS[g]["units"]]
        jobs += [(g, i + 1, t, th, titles) for i, (t, th) in enumerate(BOOKS[g]["units"])]
    with ThreadPoolExecutor(int(os.environ.get("WORKERS", 4))) as ex:
        for r in ex.map(lambda j: make(*j), jobs):
            print(r, flush=True)
