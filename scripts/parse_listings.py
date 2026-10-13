#!/usr/bin/env python3
"""Parse saved conference listing pages (virtual sites + award pages) into
data/candidates.jsonl: one line per paper {venue, year, track, title, authors, src}."""
import json, re, sys, html
from pathlib import Path
from bs4 import BeautifulSoup

LISTS = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.parent.mkdir(parents=True, exist_ok=True)
rows = []

def virtual(fname, venue, year, track):
    soup = BeautifulSoup((LISTS / fname).read_text(errors="ignore"), "lxml")
    n = 0
    for h3 in soup.select("h3.event-title"):
        a = h3.find("a")
        if not a: continue
        card = h3.find_parent()
        sp = card.select_one(".event-speakers") if card else None
        badge = card.select_one(".event-type-badge") if card else None
        rows.append(dict(venue=venue, year=year, track=track if track else (badge.get_text(strip=True) if badge else "oral"),
                         title=html.unescape(a.get_text(" ", strip=True)),
                         authors=sp.get_text(" ", strip=True).replace(" ⋅ ", ", ") if sp else "",
                         src=f"{fname}:{a.get('href')}"))
        n += 1
    print(f"{fname:22s} {n:4d}")

for y in (2024, 2025, 2026): virtual(f"iclr{y%100}_oral.html", "ICLR", y, "oral")
for y in (2024, 2025):       virtual(f"nips{y%100}_oral.html", "NeurIPS", y, "oral")
for y in (2024, 2025, 2026): virtual(f"icml{y%100}_oral.html", "ICML", y, "oral")
for y in (2025, 2026):       virtual(f"cvpr{y%100}_oral.html", "CVPR", y, "oral")
virtual("cvpr25_award.html", "CVPR", 2025, "award-candidate")
virtual("cvpr26_award.html", "CVPR", 2026, "award-candidate")
virtual("iccv25_oral.html", "ICCV", 2025, "oral")
virtual("eccv24_oral.html", "ECCV", 2024, "oral")

def text_page(fname, venue, year, track, pattern):
    soup = BeautifulSoup((LISTS / fname).read_text(errors="ignore"), "lxml")
    txt = soup.get_text("\n")
    n = 0
    for m in re.finditer(pattern, txt):
        t = m.group(1).strip()
        if 15 < len(t) < 220:
            rows.append(dict(venue=venue, year=year, track=track, title=t, authors="", src=fname)); n += 1
    print(f"{fname:22s} {n:4d}")

# award pages: titles are usually bold/quoted lines; be permissive, dedupe later by resolving on S2
for fname, venue, year in [("acl25_awards.html","ACL",2025),("acl24_awards.html","ACL",2024),
                           ("emnlp25_awards.html","EMNLP",2025),("emnlp24_awards.html","EMNLP",2024)]:
    soup = BeautifulSoup((LISTS / fname).read_text(errors="ignore"), "lxml")
    n = 0
    for el in soup.select("li, p, strong, b, h3, h4, td"):
        t = el.get_text(" ", strip=True)
        if 15 < len(t) < 200 and re.search(r"[A-Za-z]{3}", t) and not re.search(r"^(Best|Outstanding|Award|Winner|Honou?rable|Resource|Theme|Social|Test|SAC|The |Area|Paper)\b", t) and el.find("a") is None and t.count(",") < 3 and not t.endswith("."):
            rows.append(dict(venue=venue, year=year, track="award", title=t, authors="", src=fname)); n += 1
    print(f"{fname:22s} {n:4d} (raw, needs resolve)")

for fname, venue, year in [("icra25_awards.html","ICRA",2025),("icra24_awards.html","ICRA",2024),("iros24_awards.html","IROS",2024)]:
    soup = BeautifulSoup((LISTS / fname).read_text(errors="ignore"), "lxml")
    n = 0
    for el in soup.select("li, p, strong, b, em, h3, h4, h5, td"):
        t = el.get_text(" ", strip=True)
        if 20 < len(t) < 200 and re.search(r"[A-Za-z]{3}", t) and not re.search(r"^(Best|Award|Winner|Finalist|Honou?rable|IEEE|ICRA|IROS|Sponsored|The |Congratulations)", t) and t.count(",") < 3 and not t.endswith("."):
            rows.append(dict(venue=venue, year=year, track="award", title=t, authors="", src=fname)); n += 1
    print(f"{fname:22s} {n:4d} (raw, needs resolve)")

seen = set(); out = []
for r in rows:
    k = re.sub(r"\W+", "", r["title"].lower())
    if k in seen: continue
    seen.add(k); out.append(r)
OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n")
print("total unique:", len(out))
