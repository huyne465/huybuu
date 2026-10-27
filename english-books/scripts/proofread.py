"""Second pass: an editor model proofreads every unit and fixes mistakes in place.

Usage: python3 scripts/proofread.py [grade ...]
Each unit is proofread once (marked with "proofread": true); the editor's change list is kept
in the unit under "edits" so a teacher can see what changed.
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gen_content import call, validate
from topics import BOOKS

ROOT = Path(__file__).resolve().parent.parent

PROMPT = """You are the senior editor of ROXY ENGLISH, a coursebook for Vietnamese primary pupils
(Grade {grade}, {level}). Proofread this unit JSON and return the corrected unit as JSON with
EXACTLY the same keys, list lengths and structure, plus one extra key "edits": a list of short
strings describing each change you made.

Fix only real problems:
- English grammar, spelling, punctuation, unnatural phrasing, level-inappropriate words.
- Logic/consistency: names, ages, family relations, numbers and facts must agree between the
  text, its questions, its true_false answers, the conversations and the listening questions.
  Every question must be answerable from its text. True/false answers must be correct.
- IPA (American English, slashes) must match the word exactly (plural -s, etc.).
- Vietnamese: natural, correct, full diacritics, child-friendly; translations must match.
- fun_facts must be true; replace any doubtful fact with a well-known true one.
- review.mcq: exactly one correct option, and "answer" must equal that option text.
- review.order: the answer must use exactly the given words.
- riddles and odd_one_out must have one clear answer.
- emoji fields must be real emoji that match the word.
Keep everything else as it is. Do not shorten texts.

UNIT JSON:
{unit}"""


def proofread(path, grade):
    u = json.loads(path.read_text())
    if u.get("proofread"):
        return f"skip {path}"
    keep = {k: u.pop(k) for k in ("unit", "grade", "validation") if k in u}
    prompt = PROMPT.format(grade=grade, level=BOOKS[grade]["level"], unit=json.dumps(u, ensure_ascii=False))
    for attempt in range(4):
        try:
            fixed = call(prompt)
        except Exception as e:  # busy model / malformed JSON: wait and retry
            err = repr(e)[:100]
            time.sleep(20 * (attempt + 1))
            continue
        if isinstance(fixed, list) and len(fixed) == 1:
            fixed = fixed[0]
        if not isinstance(fixed, dict):
            err = "not an object"
            continue
        err = validate(fixed)
        if set(fixed) - {"edits"} == set(u) and len(err) <= len(validate(u)):
            fixed.update(keep, proofread=True)
            path.write_text(json.dumps(fixed, ensure_ascii=False, indent=1))
            return f"G{grade} {path.stem}: {len(fixed.get('edits', []))} edits"
        err = err or f"keys changed: {set(fixed) ^ set(u)}"
    return f"G{grade} {path.stem}: FAILED {err}"


if __name__ == "__main__":
    grades = [int(g) for g in sys.argv[1:]] or list(BOOKS)
    jobs = [(f, g) for g in grades for f in sorted((ROOT / f"content/grade{g}").glob("unit*.json"))]
    with ThreadPoolExecutor(int(os.environ.get("WORKERS", 3))) as ex:
        for r in ex.map(lambda j: proofread(*j), jobs):
            print(r, flush=True)
