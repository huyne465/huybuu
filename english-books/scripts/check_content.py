"""List problems in content/*.json that need a human fix before printing."""
import json
import re
import sys
from pathlib import Path

from build_book import emoji
from gen_content import validate
from topics import BOOKS

ROOT = Path(__file__).resolve().parent.parent
VI_MARKS = re.compile("[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", re.I)


def check(path, grade):
    u = json.loads(path.read_text())
    probs = validate(u)
    for i, v in enumerate(u["vocabulary"]):
        if emoji(v.get("emoji"), None) is None:
            probs.append(f"vocab emoji {i} {v['en']!r}: {v.get('emoji')!r}")
        if not v["ipa"].startswith("/"):
            probs.append(f"ipa {v['en']}: {v['ipa']}")
    words = [v["en"].lower() for v in u["vocabulary"]]
    if len(set(words)) != len(words):
        probs.append("duplicate vocabulary")
    targets = BOOKS[grade]["reading_words"]
    for r, t in zip(u["readings"], targets):
        n = len(r["text"].split())
        if not 0.7 * t <= n <= 1.4 * t:
            probs.append(f"reading {r['level']} has {n} words (target {t})")
    for w in u["brain_games"]["word_search"]:
        if not re.fullmatch("[A-Za-z]{2,10}", w):
            probs.append(f"word_search word {w!r}")
    for field in ("goal_vi", "message_vi"):
        if not VI_MARKS.search(u[field]):
            probs.append(f"{field} lacks Vietnamese diacritics")
    return probs


if __name__ == "__main__":
    total = 0
    for g in [int(x) for x in sys.argv[1:]] or list(BOOKS):
        for f in sorted((ROOT / f"content/grade{g}").glob("unit*.json")):
            for p in check(f, g):
                total += 1
                print(f"G{g} {f.stem}: {p}")
    print(f"{total} problem(s)")
