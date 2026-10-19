#!/usr/bin/env python3
"""Regenerate the index tables in README.md from ideas/*.md.

Each idea block starts with "## 💡 Idea X.Y — *Title*" and contains a table with
🎯 源论文, ⭐ Novelty, 🚀 Impact, 🧗 Difficulty rows. The index is written between
<!-- INDEX:START --> and <!-- INDEX:END -->; the 💡 Ideas badge count is updated.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CAT_NAMES = {
 "01-llm-reasoning-rl": "🧠 LLM Reasoning & RL Post-Training",
 "02-alignment-safety": "🛡️ Alignment, Safety & Interpretability",
 "03-diffusion-generative": "🌊 Diffusion & Generative Models (incl. Diffusion LLMs)",
 "04-multi-agent-systems": "🤝 Multi-Agent Systems & LLM Agents",
 "05-embodied-robotics": "🤖 Embodied AI & Robotics",
 "06-vision-3d": "👁️ Computer Vision & 3D",
 "07-multimodal-vlm": "🖼️ Multimodal & Vision-Language Models",
 "08-architecture-efficiency": "⚙️ Architecture, Efficiency & Scaling",
 "09-nlp-language": "🗣️ NLP & Language Understanding",
 "10-theory-optimization": "📐 Theory, Optimization & Learning",
 "11-ai4science-other": "🔬 AI for Science & Others",
 "12-web-search-datamining": "🌐 Web, Search, Recommendation & Data Mining",
 "13-world-models": "🌍 World Models & Video Simulation",
 "14-databases": "🗄️ Databases & Data Systems",
 "15-systems": "🖥️ Computer Systems & ML Systems",
 "16-networking": "📡 Computer Networking",
 "17-security": "🔐 Security & Privacy",
 "18-graphics": "🎨 Computer Graphics",
 "19-llm-agents": "🧭 LLM Agents: Tools, GUI/Web, Coding & Memory",
}

def slug(h):
    h = h.lower(); h = re.sub(r"[^\w\- ]", "", h); return h.replace(" ", "-")

def short_source(cell):
    # "**Title** · Authors · 🏆 Venue Year Award · [arXiv]..." -> "Title · 🏆 Venue Year"
    parts = [p.strip() for p in cell.split(" · ")]
    out = []
    for p in parts:
        p = re.sub(r"\[arXiv[^\]]*\]\([^)]*\)", "", p).strip(" ·")
        if not p: continue
        if p.startswith("**"): out.append(p.strip("*"))
        elif re.search(r"🏆|🥈|🏅|🎤|📈|📄", p): out.append(p)
    return " · ".join(out)[:140]

def parse(md):
    ideas = []
    blocks = re.split(r"\n(?=## 💡 Idea )", md)
    for b in blocks:
        m = re.match(r"## 💡 Idea ([\d.]+) — \*(.+?)\*\s*$", b.split("\n")[0])
        if not m: continue
        num, title = m.group(1), m.group(2)
        def cell(label):
            mm = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*(.+?)\s*\|\s*$", b, re.M)
            return mm.group(1).strip() if mm else ""
        venue = cell("📮 **投稿建议**")
        fields = re.findall(r"(🧪|👁️|🗣️|🎬|🌐|🤖|🧩|🔐|🎨|🎙️|🧑‍💻|🔬|🗄️|🖥️|📡|🔎)\s*\**([A-Za-z]+)\**", venue)
        ideas.append(dict(num=num, title=title, anchor=slug(b.split("\n")[0][3:]),
                          source=short_source(cell("🎯 **源论文**")), nov=cell("⭐ Novelty")[:5], imp=cell("🚀 Impact")[:5], dif=cell("🧗 Difficulty")[:5],
                          venue=venue, fields=[f"{e} {l}" for e, l in fields], primary=(fields[0][0] + " " + fields[0][1]) if fields else ""))
    return ideas

def link_title(t):
    # bold the part before ':' to keep tables scannable
    if ":" in t:
        a, b = t.split(":", 1); return f"**{a.strip()}**:{b}"
    return f"**{t}**"

toc, sections, total, by_field, all_ideas = [], [], 0, {}, []
for f in sorted((ROOT / "ideas").glob("*.md")):
    cid = f.stem; name = CAT_NAMES.get(cid, cid)
    ideas = parse(f.read_text(encoding="utf-8"))
    if not ideas: continue
    total += len(ideas); n = int(cid.split("-")[0]); all_ideas.extend(ideas)
    toc.append(f"| {n} | {name} | {len(ideas)} | [ideas/{cid}](ideas/{f.name}) |")
    rows = "\n".join(f"| [{link_title(i['title'])}](ideas/{f.name}#{i['anchor']}) | {i['source']} | {' · '.join(i['fields'])} | {i['nov']} | {i['imp']} | {i['dif']} |" for i in ideas)
    sections.append(f"## {name.split(' ',1)[0]} {n} · {name.split(' ',1)[1]}\n\n| 💡 Idea（点击查看完整分析） | 🎯 源论文 | 📮 投稿领域 | ⭐ | 🚀 | 🧗 |\n|:--|:--|:--|:--:|:--:|:--:|\n{rows}\n\n<div align=\"right\"><a href=\"#top\">🔝</a></div>\n")
    for i in ideas:
        for k, fl in enumerate(i["fields"]):
            by_field.setdefault(fl, []).append((i["num"], f"ideas/{f.name}#{i['anchor']}", k == 0, i["title"]))

FIELD_ORDER = ["🧪 ML", "👁️ CV", "🗣️ NLP", "🎬 MM", "🌐 WWW", "🔎 IR", "🤖 Robotics", "🗄️ DB", "🖥️ Systems", "📡 Networking", "🔐 Security", "🎨 Graphics", "🧩 AI", "🎙️ Speech", "🧑‍💻 HCI", "🔬 Science"]
FIELD_VENUES = {"🧪 ML": "ICLR / ICML / NeurIPS", "👁️ CV": "CVPR / ICCV / ECCV", "🗣️ NLP": "ACL / EMNLP / NAACL", "🎬 MM": "ACM MM",
                "🌐 WWW": "WWW / KDD / CIKM", "🔎 IR": "SIGIR / CIKM / ECIR", "🤖 Robotics": "ICRA / IROS / RSS / CoRL", "🗄️ DB": "SIGMOD / VLDB / ICDE", "🖥️ Systems": "OSDI / SOSP / EuroSys / MLSys", "📡 Networking": "SIGCOMM / NSDI / MobiCom", "🧩 AI": "AAAI / IJCAI", "🔐 Security": "USENIX Security / S&P / CCS",
                "🎨 Graphics": "SIGGRAPH / SIGGRAPH Asia", "🎙️ Speech": "ICASSP / Interspeech", "🧑‍💻 HCI": "CHI / CSCW", "🔬 Science": "领域期刊 / ML4H / Bioinformatics"}
field_rows = []
field_lists = []
for fl in FIELD_ORDER:
    items = by_field.get(fl, [])
    if not items: continue
    prim = [x for x in items if x[2]]; sec = [x for x in items if not x[2]]
    field_rows.append(f"| {fl} | {FIELD_VENUES[fl]} | **{len(prim)}** | {len(sec)} | {len(items)} |")
    links = lambda xs: " · ".join(f"[{num}]({href} \"{t}\")" for num, href, _, t in xs)
    field_lists.append(f"<details>\n<summary><b>{fl}</b> · {FIELD_VENUES[fl]} — 首选 {len(prim)} 条，备选 {len(sec)} 条</summary>\n\n**首选投稿**：{links(prim) or '—'}\n\n**备选投稿**：{links(sec) or '—'}\n\n</details>\n")
VENUES = [("🧪 ML", ["ICLR", "ICML", "NeurIPS", "COLT", "MLSys"]), ("👁️ CV", ["CVPR", "ICCV", "ECCV", "ICCP", "MICCAI"]),
          ("🗣️ NLP", ["ACL", "EMNLP", "NAACL"]), ("🎬 MM", ["ACM MM"]), ("🌐 WWW", ["WWW", "KDD", "CIKM"]), ("🔎 IR", ["SIGIR", "ECIR"]),
          ("🤖 Robotics", ["ICRA", "IROS", "RSS", "CoRL"]), ("🗄️ DB", ["SIGMOD", "VLDB", "ICDE"]), ("🖥️ Systems", ["OSDI", "SOSP", "EuroSys", "ATC", "FAST"]),
          ("📡 Networking", ["SIGCOMM", "NSDI", "MobiCom", "INFOCOM"]), ("🔐 Security", ["USENIX Security", "S&P", "CCS", "NDSS"]),
          ("🎨 Graphics", ["SIGGRAPH", "SIGGRAPH Asia"]), ("🧩 AI", ["AAAI", "IJCAI", "FAccT"]), ("🎙️ Speech", ["ICASSP", "Interspeech"]), ("🧑‍💻 HCI", ["CHI", "CSCW", "ASSETS"])]
def venue_hits(venue_cell, v):
    if v == "SIGGRAPH": return len(re.findall(r"SIGGRAPH(?! Asia)", venue_cell))
    if v == "S&P": return len(re.findall(r"(?<!\w)S&P", venue_cell))
    if v == "ATC": return len(re.findall(r"USENIX ATC|(?<!\w)ATC", venue_cell))
    return len(re.findall(r"(?<![\w-])" + re.escape(v) + r"(?![\w-])", venue_cell))
venue_rows = []
for fl, vs in VENUES:
    for v in vs:
        prim = sum(1 for i in all_ideas if venue_hits(i["venue"].split("＋")[0], v))
        tot = sum(1 for i in all_ideas if venue_hits(i["venue"], v))
        if tot: venue_rows.append(f"| {fl} | **{v}** | **{prim}** | {tot} |")
venue_index = ("### 🏛️ 按会议统计\n\n「首选」= 该会议出现在加粗的首选领域里；「合计」= 首选或备选中出现过。\n\n| 领域 | 会议 | 首选 | 合计 |\n|:--|:--|:--:|:--:|\n" + "\n".join(venue_rows) + "\n\n")
field_index = ("## 📮 按投稿领域索引\n\n每条 idea 的表格里都有一行 **📮 投稿建议**（加粗者为首选领域）。下表按领域汇总，展开可见各条编号（悬停显示标题）。\n\n"
               "| 领域 | 代表会议 | 首选 | 备选 | 合计 |\n|:--|:--|:--:|:--:|:--:|\n" + "\n".join(field_rows) + "\n\n" + "\n".join(field_lists) + "\n" + venue_index)
index = ("## 🗂️ 目录\n\n| # | 类别 | 💡 数量 | 直达 |\n|:--:|:--|:--:|:--|\n" + "\n".join(toc) + "\n\n" + field_index + "\n---\n\n" + "\n".join(sections))
md = README.read_text(encoding="utf-8")
new = re.sub(r"<!-- INDEX:START -->.*?<!-- INDEX:END -->", "<!-- INDEX:START -->\n" + index + "<!-- INDEX:END -->", md, flags=re.S)
new = re.sub(r"💡_Ideas-\d+-", f"💡_Ideas-{total}-", new)
new = re.sub(r"🗂️_Categories-\d+-", f"🗂️_Categories-{len(toc)}-", new)
if "--check" in sys.argv:
    for f in sorted((ROOT / "ideas").glob("*.md")):
        print(f.name, len(parse(f.read_text(encoding="utf-8"))))
    print(f"ideas={total} categories={len(toc)} (check only, README not written)")
else:
    README.write_text(new, encoding="utf-8")
    print(f"ideas={total} categories={len(toc)}")
