#!/usr/bin/env python3
"""Resolve candidates to arXiv papers and harvest their Limitation / Future Work /
Discussion sections.

  python3 scripts/harvest.py data/candidates.jsonl data/papers.jsonl

Thread A: Semantic Scholar title match -> arXiv id, citations, fields.
Thread B: arXiv HTML (fallback PDF) -> section excerpts.
Resumable: already-processed titles in the output are skipped.
"""
import json, re, sys, time, threading, queue, subprocess, tempfile, html as htmlmod
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
UA = {"User-Agent": "awesome-research-ideas-harvester/0.1 (mailto:mu.chen@mbzuai.ac.ae)"}
S2 = "https://api.semanticscholar.org/graph/v1/paper/search/match"
FIELDS = "title,externalIds,citationCount,year,fieldsOfStudy,tldr,venue"
SEC_RE = re.compile(r"(limitation|future (work|direction|research)|discussion|broader impact|conclusion|open (problem|question)|societal impact|failure case)", re.I)

done = set()
if OUT.exists():
    for line in OUT.read_text().splitlines():
        try: done.add(json.loads(line)["title_key"])
        except Exception: pass

def key(t): return re.sub(r"\W+", "", t.lower())[:80]
def jacc(a, b):
    A, B = set(re.findall(r"\w+", a.lower())), set(re.findall(r"\w+", b.lower()))
    return len(A & B) / max(1, len(A | B))

lock = threading.Lock()
def emit(rec):
    with lock:
        with OUT.open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def s2_match(title):
    for attempt in range(6):
        try:
            r = requests.get(S2, params={"query": title, "fields": FIELDS}, headers=UA, timeout=30)
            if r.status_code == 429:
                return None
            if r.status_code == 404: return None
            r.raise_for_status()
            d = r.json().get("data") or []
            return d[0] if d else None
        except Exception as e:
            time.sleep(3 + 3 * attempt)
    return None

def arxiv_search(title):
    clean = re.sub(r"[^\w\s]", " ", title).strip()
    words = [w for w in clean.split() if len(w) > 2 and w.lower() not in {"and","the","for","with","from","via","into","over","under","using","towards","toward","through","what","when","how","why","are","can","does"}]
    queries = ['ti:"%s"' % clean, " AND ".join(f"ti:{w}" for w in words[:7])]
    for q in queries:
        try:
            r = requests.get("https://export.arxiv.org/api/query", params={"search_query": q, "max_results": 3}, headers=UA, timeout=30)
            soup = BeautifulSoup(r.text, "xml")
            for e in soup.find_all("entry"):
                t = e.title.get_text(" ", strip=True)
                if jacc(t, title) >= 0.6:
                    return re.sub(r"v\d+$", "", e.id.get_text().split("/abs/")[-1]), t
        except Exception: pass
        time.sleep(1.5)
    return None, None

def sections_from_html(text):
    soup = BeautifulSoup(text, "lxml")
    out = {}
    for h in soup.find_all(re.compile("^h[2-4]$")):
        ht = h.get_text(" ", strip=True)
        if not SEC_RE.search(ht): continue
        buf = []
        for sib in h.find_all_next():
            if sib.name and re.match(r"^h[1-4]$", sib.name) and sib is not h: break
            if sib.name == "p" and not sib.find_parent("figure"):
                t = sib.get_text(" ", strip=True)
                if t: buf.append(t)
            if sum(map(len, buf)) > 3500: break
        if buf: out[ht[:80]] = " ".join(buf)[:3500]
    abst = soup.select_one("div.ltx_abstract")
    return out, (abst.get_text(" ", strip=True)[:1500] if abst else "")

def sections_from_pdf(pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f: f.write(pdf_bytes); p = f.name
    try: txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=120).stdout
    except Exception: return {}
    out = {}
    for m in re.finditer(r"\n\s*(?:\d+(?:\.\d+)*\.?\s+)?([A-Z][A-Za-z ,&/-]{3,60})\n", txt):
        ht = m.group(1).strip()
        if SEC_RE.search(ht):
            seg = txt[m.end(): m.end() + 4000]
            nxt = re.search(r"\n\s*(?:\d+(?:\.\d+)*\.?\s+)?[A-Z][A-Za-z ,&/-]{3,60}\n", seg[200:])
            if nxt: seg = seg[: 200 + nxt.start()]
            seg = re.sub(r"\s+", " ", seg).strip()
            if len(seg) > 200: out[ht[:80]] = seg[:3500]
    return out

def fetch_arxiv(aid):
    time.sleep(2.0)
    try:
        r = requests.get(f"https://arxiv.org/html/{aid}", headers=UA, timeout=60)
        if r.status_code == 200 and "ltx_document" in r.text:
            secs, abst = sections_from_html(r.text)
            if secs: return secs, abst, "html"
    except Exception: pass
    time.sleep(2.0)
    try:
        r = requests.get(f"https://export.arxiv.org/pdf/{aid}", headers=UA, timeout=120)
        if r.status_code == 200: return sections_from_pdf(r.content), "", "pdf"
    except Exception: pass
    return {}, "", "none"

q = queue.Queue()
def resolver():
    for line in SRC.read_text().splitlines():
        c = json.loads(line); k = key(c["title"])
        if k in done: continue
        rec = dict(c, title_key=k)
        aid, t = arxiv_search(c["title"]); time.sleep(1.5)
        if aid:
            rec["arxiv"] = aid; rec["s2_title"] = t
        elif c["track"] == "award":
            rec["dropped"] = "no-match"; emit(rec); continue   # noisy award-page lines
        else:
            m = s2_match(c["title"]); time.sleep(1.0)
            if m and jacc(m.get("title", ""), c["title"]) >= 0.55:
                rec.update(s2_title=m["title"], citations=m.get("citationCount"), fields=m.get("fieldsOfStudy"),
                           arxiv=(m.get("externalIds") or {}).get("ArXiv"))
        q.put(rec)
    q.put(None)

def fetcher():
    while True:
        rec = q.get()
        if rec is None: break
        if rec.get("arxiv"):
            secs, abst, how = fetch_arxiv(rec["arxiv"])
            rec.update(sections=secs, abstract=abst, fulltext=how)
        else:
            rec.update(sections={}, fulltext="no-arxiv")
        emit(rec)
        print(f"[{len(done)+q.qsize():5d}] {rec['venue']} {rec['year']} {rec.get('arxiv')} secs={len(rec.get('sections',{}))} {rec['title'][:60]}", flush=True)

NF = 3
ta = threading.Thread(target=resolver, daemon=True); ta.start()
tbs = [threading.Thread(target=fetcher, daemon=True) for _ in range(NF)]
for t in tbs: t.start()
ta.join()
for _ in range(NF - 1): q.put(None)
for t in tbs: t.join()
print("DONE")
