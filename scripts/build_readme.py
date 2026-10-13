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
        elif re.search(r"🏆|🥈|🏅|🎤|📈", p): out.append(p)
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
        ideas.append(dict(num=num, title=title, anchor=slug(b.split("\n")[0][3:]),
                          source=short_source(cell("🎯 **源论文**")), nov=cell("⭐ Novelty")[:5], imp=cell("🚀 Impact")[:5], dif=cell("🧗 Difficulty")[:5]))
    return ideas

def link_title(t):
    # bold the part before ':' to keep tables scannable
    if ":" in t:
        a, b = t.split(":", 1); return f"**{a.strip()}**:{b}"
    return f"**{t}**"

toc, sections, total = [], [], 0
for f in sorted((ROOT / "ideas").glob("*.md")):
    cid = f.stem; name = CAT_NAMES.get(cid, cid)
    ideas = parse(f.read_text(encoding="utf-8"))
    if not ideas: continue
    total += len(ideas); n = int(cid.split("-")[0])
    toc.append(f"| {n} | {name} | {len(ideas)} | [ideas/{cid}](ideas/{f.name}) |")
    rows = "\n".join(f"| [{link_title(i['title'])}](ideas/{f.name}#{i['anchor']}) | {i['source']} | {i['nov']} | {i['imp']} | {i['dif']} |" for i in ideas)
    sections.append(f"## {name.split(' ',1)[0]} {n} · {name.split(' ',1)[1]}\n\n| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |\n|:--|:--|:--:|:--:|:--:|\n{rows}\n\n<div align=\"right\"><a href=\"#top\">🔝</a></div>\n")

index = ("## 🗂️ 目录\n\n| # | 类别 | 💡 数量 | 直达 |\n|:--:|:--|:--:|:--|\n" + "\n".join(toc) + "\n\n---\n\n" + "\n".join(sections))
md = README.read_text(encoding="utf-8")
new = re.sub(r"<!-- INDEX:START -->.*?<!-- INDEX:END -->", "<!-- INDEX:START -->\n" + index + "<!-- INDEX:END -->", md, flags=re.S)
new = re.sub(r"💡_Ideas-\d+-", f"💡_Ideas-{total}-", new)
new = re.sub(r"🗂️_Categories-\d+-", f"🗂️_Categories-{len(toc)}-", new)
README.write_text(new, encoding="utf-8")
print(f"ideas={total} categories={len(toc)}")
