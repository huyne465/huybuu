"""Lay out one PDF book per grade from content/*.json (+ images/ when present).

Usage: python3 scripts/build_book.py [grade ...]   -> output/ROXY_English_Grade_<n>.pdf
Pictures missing from images/ fall back to colourful emoji illustrations.
"""
import html
import json
import random
import re
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from topics import BOOKS

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "output"

SECTIONS = [
    ("BIG QUESTION", "Câu hỏi lớn", "💭", "Khởi động: suy nghĩ và chia sẻ về chủ đề."),
    ("VOCABULARY", "Từ vựng", "🖼️", "20 thẻ từ có hình, phiên âm và nghĩa tiếng Việt."),
    ("PHONICS FUN", "Ngữ âm vui", "🔤", "Luyện một âm mới qua từ và câu nói líu lưỡi."),
    ("SENTENCE PATTERNS", "Mẫu câu", "🧩", "8 mẫu câu trọng tâm kèm ví dụ."),
    ("GRAMMAR IN USE", "Ngữ pháp", "⚙️", "Giải thích dễ hiểu, câu đúng ✅ và câu sai ❌."),
    ("SING & CHANT", "Hát và vè", "🎵", "Bài hát theo giai điệu quen thuộc, kèm động tác."),
    ("READING 1 – EASY", "Đọc hiểu 1 – Dễ", "📖", "Bài đọc ngắn, từ vựng và 10 câu hỏi."),
    ("READING 2 – MORE PRACTICE", "Đọc hiểu 2 – Luyện thêm", "📗", "Bài đọc dài hơn, đúng/sai và câu hỏi."),
    ("READING 3 – CHALLENGE", "Đọc hiểu 3 – Thử thách", "📘", "Bài đọc thử thách cho học sinh khá giỏi."),
    ("COMIC STORY", "Truyện tranh", "💬", "Câu chuyện vui 4 khung tranh để đọc phân vai."),
    ("SPEAK UP!", "Nói", "🎤", "15 câu hỏi gợi ý, bài nói mẫu và thử thách nói."),
    ("REAL-LIFE CONVERSATIONS", "Hội thoại thực tế", "🗣️", "2 đoạn hội thoại để luyện theo cặp."),
    ("LISTEN & RESPOND", "Nghe và trả lời", "🎧", "Giáo viên đọc bài nghe, học sinh trả lời."),
    ("BRAIN GAMES", "Trò chơi trí tuệ", "🧠", "Tìm từ, xếp chữ, câu đố, tìm từ khác loại."),
    ("LET'S PLAY TOGETHER", "Trò chơi cả lớp", "🎲", "Trò chơi tương tác cho cả lớp hoặc nhóm."),
    ("WRITE ABOUT YOU", "Viết về em", "✍️", "Hồ sơ cá nhân và khung viết đoạn văn."),
    ("LIFE SKILL & VALUE", "Kỹ năng sống", "💖", "Thói quen tốt và câu hỏi giá trị ROXY."),
    ("DID YOU KNOW?", "Em có biết?", "🌍", "5 sự thật thú vị mở rộng hiểu biết."),
    ("ROXY PROJECT", "Dự án ROXY", "🎨", "Vẽ – viết – thuyết trình sản phẩm của em."),
    ("REVIEW & I CAN…", "Ôn tập & tự đánh giá", "✅", "Bài ôn tập 4 phần và bảng tự đánh giá."),
]

EMOJI_ONE = (r"[\u2190-\u21FF\U0001F000-\U0001FAFF☀-➿⬀-⯿⌀-⏿〰〽㊗㊙]"
             r"(?:️|[\U0001F3FB-\U0001F3FF]|‍[\U0001F000-\U0001FAFF☀-➿]️?)*")
EMOJI_RE = re.compile(f"^(?:{EMOJI_ONE})+$")


def e(s):
    return html.escape(str(s))


def emoji(s, default="⭐"):
    s = (s or "").strip()
    return s if s and EMOJI_RE.match(s) else default


def img_or(path, fallback_html, cls=""):
    if path.exists():
        return f'<img class="{cls}" src="{path.as_uri()}">'
    return fallback_html


def emoji_scene(emojis, cls="scene", seed=0):
    """Colourful sticker collage used when an AI illustration is not available yet."""
    rnd = random.Random(seed)
    items = []
    for i, em in enumerate(emojis[:9]):
        x, y = (i % 3) * 31 + rnd.randint(2, 10), (i // 3) * 30 + rnd.randint(2, 8)
        size, rot = rnd.choice([2.4, 2.9, 3.4]), rnd.randint(-18, 18)
        items.append(f'<span style="left:{x}%;top:{y}%;font-size:{size}em;transform:rotate({rot}deg)">{em}</span>')
    return f'<div class="{cls} emoji-scene">{"".join(items)}</div>'


def lines(n, cls="wline"):
    return "".join(f'<div class="{cls}"></div>' for _ in range(n))


def word_search(words, grade, seed):
    rnd = random.Random(seed)
    words = [re.sub("[^A-Z]", "", w.upper()) for w in words][:8]
    size = max(10, max(map(len, words)) + 1)
    dirs = [(0, 1), (1, 0)] + ([(1, 1)] if grade >= 3 else [])
    grid = [[""] * size for _ in range(size)]
    for w in sorted(words, key=len, reverse=True):
        for _ in range(500):
            dr, dc = rnd.choice(dirs)
            r = rnd.randrange(size - dr * (len(w) - 1))
            c = rnd.randrange(size - dc * (len(w) - 1))
            cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
            if all(grid[a][b] in ("", w[i]) for i, (a, b) in enumerate(cells)):
                for i, (a, b) in enumerate(cells):
                    grid[a][b] = w[i]
                break
    alpha = "ABCDEFGHIJKLMNOPRSTUVWY"
    rows = "".join("<tr>" + "".join(f"<td>{ch or rnd.choice(alpha)}</td>" for ch in row) + "</tr>"
                   for row in grid)
    return f'<table class="wsearch">{rows}</table>', words


def scramble(word, seed):
    letters = list(word.lower())
    rnd = random.Random(seed)
    for _ in range(50):
        rnd.shuffle(letters)
        if "".join(letters) != word.lower() or len(set(word)) < 2:
            break
    return " ".join(letters)


def sec_head(n, extra=""):
    en, vi, icon, _ = SECTIONS[n - 1]
    title = extra or en
    return (f'<div class="sec-head"><span class="num">{n}</span><span class="icon">{icon}</span>'
            f'<span class="t">{e(title)}</span><span class="vi">{e(vi)}</span></div>')


def vocab_table(rows):
    body = "".join(f"<tr><td><b>{e(v['en'])}</b></td><td class='ipa'>{e(v['ipa'])}</td><td>{e(v['vi'])}</td></tr>"
                   for v in rows)
    return f'<table class="vt"><tr><th>English</th><th>Phonetic</th><th>Nghĩa tiếng Việt</th></tr>{body}</table>'


def qlist(qs, write=True, cls="qs"):
    items = "".join(f"<li>{e(q)}{'<div class=wline></div>' if write else ''}</li>" for q in qs)
    return f'<ol class="{cls}">{items}</ol>'


def unit_html(u, grade, idir):
    g = grade
    n = u["unit"]
    vemo = [emoji(v.get("emoji")) for v in u["vocabulary"]]
    seed = g * 100 + n
    cover_emo = re.findall(EMOJI_ONE, u.get("cover_emoji", "")) or vemo
    out = []

    # ---- Unit opener
    contents = "".join(f'<span title="{e(s[0])}"><b>{i + 1}</b>{s[2]}</span>' for i, s in enumerate(SECTIONS))
    bq = u["big_question"]
    out.append(f"""
<section class="opener" id="u{n}">
  <div class="mark">ROXYMARK-G{g}-U{n:02d}</div>
  <div class="unit-tag">UNIT {n}</div>
  <h1>{e(u['title'].upper())}</h1>
  <div class="theme">Theme: {e(u['theme'])} · {e(BOOKS[g]['level'])}</div>
  {img_or(idir / 'cover.jpg', emoji_scene(cover_emo + vemo, 'hero', seed), 'hero')}
  <div class="goal"><b>🎯 Goal:</b> {e(u['goal'])}<br><span class="vi-text">{e(u['goal_vi'])}</span></div>
  <div class="journey">{contents}</div>
  <div class="sec">{sec_head(1)}
  <div class="bubble big"><div class="q">{e(bq['en'])}</div><div class="vi-text">{e(bq['vi'])}</div></div>
  <p class="lead">Think and talk 🤔</p>
  <div class="grid2">{''.join(f'<div class="pill">💡 {e(p)}</div>' for p in bq['prompts'])}</div></div>
</section>""")

    # ---- 2 Vocabulary
    cards = []
    for i, v in enumerate(u["vocabulary"]):
        pic = img_or(idir / f"vocab{i:02d}.jpg", f'<div class="vemo">{vemo[i]}</div>', "vimg")
        cards.append(f'<div class="vcard">{pic}<div class="w">{e(v["en"])}</div>'
                     f'<div class="ipa">{e(v["ipa"])}</div><div class="m">{e(v["vi"])}</div></div>')
    out.append(f'<section class="sec page-start">{sec_head(2)}<div class="vgrid">{"".join(cards)}</div>'
               f'<p class="tip">👉 Point, say and spell! · Chỉ tranh, đọc to và đánh vần từ.</p></section>')

    # ---- 3 Phonics
    ph = u["phonics"]
    out.append(f"""<section class="sec">{sec_head(3)}
  <div class="phon"><div class="sound">{e(ph['sound'])}<small>{e(ph['letters'])}</small></div>
  <div class="pwords">{''.join(f'<span>{e(w)}</span>' for w in ph['words'])}</div></div>
  <div class="chant">👅 <b>Tongue twister:</b> {e(ph['chant'])}</div>
  <p class="tip">🗣️ {e(ph['tip_vi'])}</p>
</section>""")

    # ---- 4 Patterns
    pats = "".join(
        f'<div class="pat"><div class="ph">Pattern {i + 1}</div><div class="pp">{e(p["pattern"])}</div>'
        f'<div class="vi-text">{e(p["vi"])}</div><ul>{"".join(f"<li>{e(x)}</li>" for x in p["examples"])}</ul></div>'
        for i, p in enumerate(u["patterns"]))
    out.append(f'<section class="sec">{sec_head(4)}<div class="grid2 pats">{pats}</div></section>')

    # ---- 5 Grammar
    gr = "".join(
        f'<div class="gbox"><h4>{"ABCD"[i]}. {e(x["title"])}</h4><p>{e(x["explain_en"])}</p>'
        f'<p class="vi-text">🇻🇳 {e(x["explain_vi"])}</p><ul>{"".join(f"<li>{e(s)}</li>" for s in x["examples"])}</ul>'
        f'<div class="rw"><span class="ok">{e(x["right"])}</span><span class="no">{e(x["wrong"])}</span></div></div>'
        for i, x in enumerate(u["grammar"]))
    out.append(f'<section class="sec">{sec_head(5)}{gr}</section>')

    # ---- 6 Song
    s = u["song"]
    out.append(f"""<section class="sec">{sec_head(6)}
  <div class="song"><div class="stitle">🎶 {e(s['title'])}</div><div class="tune">{e(s['tune'])}</div>
  <div class="lyrics">{''.join(f'<div>{e(l)}</div>' for l in s['lines'])}</div>
  <div class="notes">🎵 🎶 🎵</div></div>
  <p class="tip">💃 {e(s['actions_vi'])}</p>
</section>""")

    # ---- 7-9 Readings
    for i, r in enumerate(u["readings"]):
        pic = img_or(idir / f"reading{i}.jpg", emoji_scene(vemo[i * 5:i * 5 + 9] or vemo, "rimg", seed + i), "rimg")
        tf = "".join(f'<tr><td>{j + 1}. {e(t["statement"])}</td><td class="box">T</td><td class="box">F</td></tr>'
                     for j, t in enumerate(r["true_false"]))
        out.append(f"""<section class="sec page-start">{sec_head(7 + i)}
  <div class="reading lvl{i}">{pic}<h2>{e(r['title'].upper())}</h2>
  {''.join(f'<p>{e(p)}</p>' for p in r['text'].split(chr(10)) if p.strip())}</div>
  <h4 class="sub">📝 Vocabulary</h4>{vocab_table(r['vocab'])}
  <h4 class="sub">✔️ True or False?</h4><table class="tf">{tf}</table>
  <h4 class="sub">❓ 10 Questions</h4>{qlist(r['questions'])}
  <div class="drawbox small">🖍️ Draw your favourite part of the story · Vẽ đoạn em thích nhất trong câu chuyện</div>
</section>""")

    # ---- 10 Comic
    c = u["comic"]
    if (idir / "comic.jpg").exists():
        comic = (f'<img class="comic-img" src="{(idir / "comic.jpg").as_uri()}"><div class="caps">'
                 + "".join(f'<div><b>{j + 1}</b> {e(p["speech"])}</div>' for j, p in enumerate(c["panels"])) + "</div>")
    else:
        comic = '<div class="comic">' + "".join(
            f'<div class="panel"><span class="pn">{j + 1}</span>{emoji_scene(vemo[j * 4:j * 4 + 4], "pscene", seed + j)}'
            f'<div class="speech">{e(p["speech"])}</div><div class="scene-desc">{e(p["scene"])}</div></div>'
            for j, p in enumerate(c["panels"])) + "</div>"
    out.append(f'<section class="sec page-start">{sec_head(10)}<h2 class="ctitle">{e(c["title"])}</h2>{comic}'
               f'<p class="tip">🎭 Read in pairs. Then act it out! · Đọc phân vai rồi diễn lại câu chuyện.</p></section>')

    # ---- 11 Speak up
    sp = u["speak_up"]
    out.append(f"""<section class="sec page-start">{sec_head(11)}
  <p class="lead">Use these questions to help you:</p>{qlist(sp['questions'], False, 'qs cols2')}
  <div class="model"><h4>🌟 Speaking Model</h4><p>{e(sp['model'])}</p></div>
  <div class="challenge">🎤 <b>Speaking Challenge:</b> {e(sp['challenge'])}</div>
</section>""")

    # ---- 12 Conversations
    convs = []
    for i, cv in enumerate(u["conversations"]):
        speakers = list(dict.fromkeys(l["speaker"] for l in cv["lines"]))
        ls = "".join(f'<div class="cl s{speakers.index(l["speaker"]) % 2}"><b>{e(l["speaker"])}:</b> {e(l["text"])}</div>'
                     for l in cv["lines"])
        pic = img_or(idir / f"conv{i}.jpg", emoji_scene(["👧", "👦", "💬"] + vemo[i * 3:i * 3 + 3], "cimg", seed + 7 + i), "cimg")
        convs.append(f'<div class="conv"><h4>Conversation {i + 1} – {e(cv["title"])}</h4>{pic}{ls}</div>')
    out.append(f'<section class="sec">{sec_head(12)}{"".join(convs)}</section>')

    # ---- 13 Listening
    li = u["listening"]
    out.append(f"""<section class="sec page-start">{sec_head(13)}
  <div class="script"><h4>👩‍🏫 Teacher's Listening Script</h4><p>{e(li['script'])}</p>
  <div class="cut">✂ Teacher reads aloud 2–3 times · Giáo viên đọc 2–3 lần</div></div>
  <h4 class="sub">🎧 Listen and Answer</h4>{qlist(li['questions'])}
</section>""")

    # ---- 14 Brain games
    bg = u["brain_games"]
    grid, words = word_search(bg["word_search"], g, seed)
    odd = "".join(f'<li>{" · ".join(e(o) for o in x["options"])}</li>' for x in bg["odd_one_out"])
    rid = "".join(f'<div class="riddle">🧩 {e(x["riddle"])}<div class="wline"></div></div>' for x in bg["riddles"])
    scr = "".join(f'<div class="scr"><span>{e(scramble(x["answer"], seed + j))}</span> → ________</div>'
                  for j, x in enumerate(bg["scramble"]))
    out.append(f"""<section class="sec page-start">{sec_head(14)}
  <div class="game"><h4>🔍 A. Word Search · Tìm từ</h4><div class="ws-wrap">{grid}
  <div class="ws-words">{''.join(f'<span>☐ {w}</span>' for w in words)}</div></div></div>
  <div class="game"><h4>🔀 B. Unscramble the Words · Sắp xếp chữ cái</h4><div class="grid2">{scr}</div></div>
  <div class="game"><h4>🚫 C. Odd One Out · Khoanh từ khác loại</h4><ol class="odd">{odd}</ol></div>
  <div class="game"><h4>❓ D. Riddles · Câu đố</h4>{rid}</div>
</section>""")

    # ---- 15 Classroom game
    cg = u["classroom_game"]
    steps = "".join(f'<li>{e(a)}<div class="vi-text">{e(b)}</div></li>' for a, b in zip(cg["steps_en"], cg["steps_vi"]))
    out.append(f"""<section class="sec">{sec_head(15)}
  <div class="cgame"><div class="cg-name">🎲 {e(cg['name'])}</div><div class="cg-players">👥 {e(cg['players'])}</div>
  <ol>{steps}</ol><div class="lang"><b>Say:</b> {' · '.join(f'“{e(x)}”' for x in cg['language'])}</div></div>
</section>""")

    # ---- 16 Write
    w = u["write"]
    prof = "".join(f'<div class="field"><b>{e(f)}</b><span></span></div>' for f in w["profile_fields"])
    frame = "".join(f"<div class='fl'>{e(x)}</div>" for x in w["frame_lines"])
    out.append(f"""<section class="sec page-start">{sec_head(16)}
  <h4 class="sub">🪪 {e(w['profile_title'])}</h4><div class="profile">{prof}</div>
  <h4 class="sub">📄 Writing Frame – {e(w['frame_title'])}</h4><div class="frame">{frame}</div>
</section>""")

    # ---- 17 Life skill
    ls = u["life_skill"]
    pic = img_or(idir / "value.jpg", emoji_scene(["💖", "🤝", "🌱", "😊", "🌈", "⭐"], "vpic", seed + 11), "vpic")
    out.append(f"""<section class="sec page-start">{sec_head(17)}<h2 class="ctitle">{e(ls['title'])}</h2>
  {pic}<p>{e(ls['intro'])}</p><p class="vi-text">{e(ls['intro_vi'])}</p>
  <div class="cando">{''.join(f'<div>✅ {e(x)}</div>' for x in ls['can_do'])}</div>
  <div class="valueq"><b>💭 ROXY VALUE QUESTION:</b> {e(ls['value_question'])}{lines(2)}</div>
</section>""")

    # ---- 18 Fun facts
    facts = "".join(f'<div class="fact"><span class="fi">{"🌟🔭🦉🌏🚀"[i % 5]}</span><div><b>{e(f["en"])}</b>'
                    f'<div class="vi-text">{e(f["vi"])}</div></div></div>' for i, f in enumerate(u["fun_facts"]))
    out.append(f'<section class="sec">{sec_head(18)}{facts}</section>')

    # ---- 19 Project
    pj = u["project"]
    pic = img_or(idir / "project.jpg", emoji_scene(["🎨", "🖍️", "✂️", "📐", "🖼️"] + vemo[:4], "vpic", seed + 13), "vpic")
    out.append(f"""<section class="sec page-start">{sec_head(19)}<h2 class="ctitle">{e(pj['title'])}</h2>
  <p class="lead">🎨 {e(pj['task'])}</p>{pic}
  <div class="step"><b>Step 1 – Draw.</b> You can draw: {', '.join(e(x) for x in pj['draw_items'])}.</div>
  <div class="step"><b>Step 2 – Write</b> 5–8 sentences. Example:<div class="example">{'<br>'.join(e(x) for x in pj['example'])}</div></div>
  <div class="step"><b>Step 3 – Present.</b> Show your poster and say: <i>“{e(pj['present'])}”</i></div>
  <div class="drawbox">My poster · Bản vẽ của em</div>
</section>""")

    # ---- 20 Review & I can
    rv = u["review"]
    comp = "".join(f"<li>{e(x['word'])}</li>" for x in rv["complete_words"])
    mcq = "".join(f'<li>{e(x["q"])}<div class="opts">{"".join(f"<span>{l}. {e(o)}</span>" for l, o in zip("abc", x["options"]))}</div></li>'
                  for x in rv["mcq"])
    order = "".join(f'<li>{e(x["words"])}<div class="wline"></div></li>' for x in rv["order"])
    ican = "".join(f"<div>☐ {e(x)}</div>" for x in u["i_can"])
    out.append(f"""<section class="sec page-start">{sec_head(20)}
  <h4 class="sub">A. Complete the Words</h4><ol class="cols5">{comp}</ol>
  <h4 class="sub">B. Choose the Correct Answer</h4><ol class="mcq cols2">{mcq}</ol>
  <h4 class="sub">C. Put the Words in Order</h4><ol class="cols2">{order}</ol>
  <h4 class="sub">D. Answer About You</h4>{qlist(rv['about_you'], True, 'qs cols2')}
  <div class="ican"><h4>⭐ I CAN… <small>Put a ✓ when you can do it.</small></h4>{ican}</div>
  <div class="message"><div class="mtag">ROXY ENGLISH – UNIT MESSAGE</div>
  <div class="men">“{e(u['message_en'])}”</div><div class="mvi">{e(u['message_vi'])}</div>
  <p>{e(u['message_body'])}</p><div class="vline">🌟 {e(u['value_line'])}</div></div>
</section>""")
    return "\n".join(out)


def answers_html(u, grade):
    seed = grade * 100 + u["unit"]
    rv, bg = u["review"], u["brain_games"]
    tf = " | ".join(f"R{i + 1}: " + ", ".join(f"{j + 1}-{'T' if t['answer'] else 'F'}" for j, t in enumerate(r["true_false"]))
                    for i, r in enumerate(u["readings"]))
    _, words = word_search(bg["word_search"], grade, seed)
    parts = [
        ("True / False", tf),
        ("Word search", ", ".join(words)),
        ("Unscramble", ", ".join(f"{j + 1}. {x['answer']}" for j, x in enumerate(bg["scramble"]))),
        ("Odd one out", "; ".join(f"{j + 1}. {x['answer']} ({x['why_vi']})" for j, x in enumerate(bg["odd_one_out"]))),
        ("Riddles", ", ".join(f"{j + 1}. {x['answer']}" for j, x in enumerate(bg["riddles"]))),
        ("Review A", ", ".join(f"{j + 1}. {x['answer']}" for j, x in enumerate(rv["complete_words"]))),
        ("Review B", ", ".join(f"{j + 1}. {'abc'[x['options'].index(x['answer'])]}" for j, x in enumerate(rv["mcq"]))),
        ("Review C", " ".join(f"{j + 1}. {x['answer']}" for j, x in enumerate(rv["order"]))),
    ]
    rows = "".join(f"<tr><th>{k}</th><td>{e(v)}</td></tr>" for k, v in parts)
    return f'<div class="akey"><h3>Unit {u["unit"]} – {e(u["title"])}</h3><table>{rows}</table></div>'


def css(color):
    return (ROOT / "scripts" / "book.css").read_text().replace("--brand-placeholder", color)


def build(grade):
    book = BOOKS[grade]
    units = [json.loads(f.read_text()) for f in sorted((ROOT / f"content/grade{grade}").glob("unit*.json"))]
    for u in units:  # titles exactly as planned in topics.py, so the contents read consistently
        u["title"] = book["units"][u["unit"] - 1][0]
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    head = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{(ROOT / "fonts/fonts.css").as_uri()}">'
            f"<style>{css(book['color'])}</style></head><body class='g{grade}'>")

    # Cover (full bleed, no footer)
    cimg = ROOT / f"images/grade{grade}/cover.jpg"
    art = img_or(cimg, emoji_scene(["📚", "🌈", "🦁", "🚀", "🎨", "⭐", "🐼", "✏️", "🎵"], "cover-art", grade), "cover-art")
    cover = f"""{head.replace("<body", "<style>@page { margin: 0; }</style><body data-cover")}<div class="cover">
  <div class="brand">ROXY ENGLISH</div><div class="grade">GRADE {grade}</div>
  <div class="sub">Student's Book · {e(book['level'])}</div>{art}
  <div class="badges"><span>📚 {len(units)} Units</span><span>🧩 20 Sections / Unit</span><span>🖼️ Picture Cards</span><span>🧠 Brain Games</span></div>
  <div class="motto">Learn English – Learn to Love – Learn to Grow</div></div></body></html>"""
    (BUILD / f"g{grade}_cover.html").write_text(cover)

    def body(page_map):
        intro = "".join(f'<div class="how"><span class="num">{i + 1}</span><span class="icon">{s[2]}</span>'
                        f'<div><b>{e(s[0])}</b> · {e(s[1])}<br><small>{e(s[3])}</small></div></div>'
                        for i, s in enumerate(SECTIONS))
        toc = "".join(
            f'<tr><td class="tu">UNIT {u["unit"]}</td><td><b>{e(u["title"])}</b><br><small>{e(u["theme"])} · '
            f'{e(", ".join(v["en"] for v in u["vocabulary"][:6]))}…</small></td>'
            f'<td class="tp">{page_map.get(u["unit"], "")}</td></tr>' for u in units)
        toc += f'<tr><td class="tu">✔</td><td><b>Answer Key</b> · Đáp án cho giáo viên</td><td class="tp">{page_map.get("key", "")}</td></tr>'
        units_html = "".join(unit_html(u, grade, ROOT / f"images/grade{grade}/unit{u['unit']:02d}") for u in units)
        key = "".join(answers_html(u, grade) for u in units)
        return f"""{head}
<section class="intro"><h1>Welcome to ROXY ENGLISH {grade}! 👋</h1>
<p>Mỗi unit trong sách gồm <b>20 phần</b> được thiết kế theo lộ trình: Khởi động → Từ vựng → Ngữ âm → Mẫu câu & Ngữ pháp →
Hát → Đọc 3 cấp độ → Truyện tranh → Nói → Hội thoại → Nghe → Trò chơi trí tuệ → Viết → Kỹ năng sống → Mở rộng → Dự án → Ôn tập.</p>
<div class="howgrid">{intro}</div></section>
<section class="toc"><h1>CONTENTS · MỤC LỤC</h1><table>{toc}</table></section>
{units_html}
<section class="answers"><div class="mark">ROXYMARK-G{grade}-KEY</div><h1>ANSWER KEY · ĐÁP ÁN</h1>{key}</section>
</body></html>"""

    label = f"ROXY ENGLISH · Grade {grade}"
    pages = {}
    for _ in range(2):  # pass 1 finds page numbers, pass 2 prints them in the contents
        (BUILD / f"g{grade}_body.html").write_text(body(pages))
        subprocess.run(["node", str(ROOT / "scripts/pdf.js"), str(BUILD / f"g{grade}_body.html"),
                        str(BUILD / f"g{grade}_body.pdf"), label], check=True)
        reader = PdfReader(BUILD / f"g{grade}_body.pdf")
        found = {}
        for i, p in enumerate(reader.pages):
            for m in re.findall(r"ROXYMARK-G\d-(U\d\d|KEY)", p.extract_text() or ""):
                found.setdefault(int(m[1:]) if m != "KEY" else "key", i + 1)
        if found == pages:
            break
        pages = found
    subprocess.run(["node", str(ROOT / "scripts/pdf.js"), str(BUILD / f"g{grade}_cover.html"),
                    str(BUILD / f"g{grade}_cover.pdf")], check=True)

    w = PdfWriter()
    w.append(str(BUILD / f"g{grade}_cover.pdf"))
    w.append(str(BUILD / f"g{grade}_body.pdf"))
    for u in units:
        if u["unit"] in pages:
            w.add_outline_item(f"Unit {u['unit']} – {u['title']}", pages[u["unit"]])  # +1 cover, 0-based
    if "key" in pages:
        w.add_outline_item("Answer Key", pages["key"])
    w.add_metadata({"/Title": f"ROXY ENGLISH – Grade {grade}", "/Author": "ROXY ENGLISH"})
    dest = OUT / f"ROXY_English_Grade_{grade}.pdf"
    with open(dest, "wb") as f:
        w.write(f)
    print(f"{dest.name}: {len(w.pages)} pages, units on pages {pages}")


if __name__ == "__main__":
    for g in [int(x) for x in sys.argv[1:]] or list(BOOKS):
        build(g)
