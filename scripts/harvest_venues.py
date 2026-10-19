#!/usr/bin/env python3
"""Harvest Limitation / Future Work / Discussion sections for papers from
systems, database, networking, security, IR and graphics venues.

  python3 scripts/harvest_venues.py candidates2.json data/papers_venues.jsonl

Resolution order: arXiv (phrase title search, then Semantic Scholar match)
-> USENIX open-access PDF (presentation page) -> direct PDF url (e.g. PVLDB).
Resumable: titles already in the output are skipped.
"""
import json, re, sys, time, subprocess, tempfile, threading, queue
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
UA = {"User-Agent": "awesome-research-ideas-harvester/0.2 (mailto:mu.chen@mbzuai.ac.ae)"}
SEC_RE = re.compile(r"(limitation|future (work|direction|research)|discussion|conclusion|open (problem|question)|lessons? learned|threats to validity|ethic)", re.I)
STOP = {"and","the","for","with","from","via","into","over","under","using","towards","toward","through","what","when","how","why","are","can","does","your","you"}

def key(t): return re.sub(r"\W+", "", t.lower())[:80]
def jacc(a, b):
    A, B = set(re.findall(r"\w+", a.lower())), set(re.findall(r"\w+", b.lower()))
    return len(A & B) / max(1, len(A | B))

done = set()
if OUT.exists():
    for l in OUT.read_text().splitlines():
        try: done.add(json.loads(l)["title_key"])
        except Exception: pass
lock = threading.Lock()
def emit(r):
    with lock:
        with OUT.open("a") as f: f.write(json.dumps(r, ensure_ascii=False) + "\n")

def arxiv_search(title):
    clean = re.sub(r"[^\w\s]", " ", title).strip()
    words = [w for w in clean.split() if len(w) > 2 and w.lower() not in STOP]
    for q in ['ti:"%s"' % clean, " AND ".join(f"ti:{w}" for w in words[:7])]:
        try:
            r = requests.get("https://export.arxiv.org/api/query", params={"search_query": q, "max_results": 3}, headers=UA, timeout=30)
            for e in BeautifulSoup(r.text, "xml").find_all("entry"):
                t = e.title.get_text(" ", strip=True)
                if jacc(t, title) >= 0.6:
                    return re.sub(r"v\d+$", "", e.id.get_text().split("/abs/")[-1]), t, e.summary.get_text(" ", strip=True)
        except Exception: pass
        time.sleep(1.2)
    return None, None, None

def s2_match(title):
    try:
        r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search/match",
                         params={"query": title, "fields": "title,externalIds,citationCount,abstract"}, headers=UA, timeout=30)
        if r.status_code != 200: return None
        d = (r.json().get("data") or [None])[0]
        return d if d and jacc(d.get("title", ""), title) >= 0.55 else None
    except Exception: return None

def sections_from_html(text):
    soup = BeautifulSoup(text, "lxml"); out = {}
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
    return out

def sections_from_pdf_bytes(b):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f: f.write(b); p = f.name
    try: txt = subprocess.run(["pdftotext", p, "-"], capture_output=True, text=True, timeout=120).stdout
    except Exception: return {}
    out = {}
    hdr = re.compile(r"\n\s*(?:\d+(?:\.\d+)*\.?\s+)?([A-Z][A-Za-z ,&/:-]{3,60})\s*\n")
    for m in hdr.finditer(txt):
        ht = m.group(1).strip()
        if not SEC_RE.search(ht) or len(ht.split()) > 8: continue
        seg = txt[m.end(): m.end() + 5000]
        nx = hdr.search(seg[300:])
        if nx: seg = seg[: 300 + nx.start()]
        seg = re.sub(r"-\n(\w)", r"\1", seg); seg = re.sub(r"\s+", " ", seg).strip()
        if len(seg) > 250: out.setdefault(ht[:80], seg[:3500])
    return out

def fetch_arxiv(aid):
    time.sleep(1.5)
    try:
        r = requests.get(f"https://arxiv.org/html/{aid}", headers=UA, timeout=60)
        if r.status_code == 200 and "ltx_document" in r.text:
            s = sections_from_html(r.text)
            if s: return s, "arxiv-html"
    except Exception: pass
    time.sleep(1.5)
    try:
        r = requests.get(f"https://export.arxiv.org/pdf/{aid}", headers=UA, timeout=120)
        if r.status_code == 200: return sections_from_pdf_bytes(r.content), "arxiv-pdf"
    except Exception: pass
    return {}, "none"

def fetch_usenix(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        soup = BeautifulSoup(r.text, "lxml")
        a = next((a for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf") and "/system/files/" in a["href"] and "slides" not in a["href"]), None)
        abst = soup.select_one(".field-name-field-paper-description")
        if not a: return {}, "none", (abst.get_text(" ", strip=True) if abst else "")
        href = a["href"] if a["href"].startswith("http") else "https://www.usenix.org" + a["href"]
        pr = requests.get(href, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
        return sections_from_pdf_bytes(pr.content), "usenix-pdf", (abst.get_text(" ", strip=True) if abst else "")
    except Exception: return {}, "none", ""

def fetch_pdf(url):
    try:
        pr = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
        if pr.status_code == 200 and pr.content[:4] == b"%PDF": return sections_from_pdf_bytes(pr.content), "direct-pdf"
    except Exception: pass
    return {}, "none"

q = queue.Queue()
def resolver():
    for c in json.loads(SRC.read_text()):
        k = key(c["title"])
        if k in done: continue
        rec = dict(c, title_key=k)
        aid, t, summ = arxiv_search(c["title"])
        if not aid:
            m = s2_match(c["title"]); time.sleep(1.0)
            if m:
                aid = (m.get("externalIds") or {}).get("ArXiv"); rec["citations"] = m.get("citationCount")
                rec["abstract"] = rec.get("abstract") or (m.get("abstract") or "")
        if aid: rec["arxiv"] = aid
        if summ and not rec.get("abstract"): rec["abstract"] = summ
        q.put(rec)

def fetcher():
    while True:
        rec = q.get()
        if rec is None: break
        secs, how = {}, "none"
        if rec.get("arxiv"): secs, how = fetch_arxiv(rec["arxiv"])
        if not secs and "usenix.org" in rec.get("url", ""):
            secs, how, ab = fetch_usenix(rec["url"]); rec["abstract"] = rec.get("abstract") or ab
        if not secs and rec.get("pdf"): secs, how = fetch_pdf(rec["pdf"])
        rec.update(sections=secs, fulltext=how); emit(rec)
        print(f"{rec['venue']:16s} {rec['year']} {how:11s} secs={len(secs)} {rec['title'][:70]}", flush=True)

NF = 4
ta = threading.Thread(target=resolver, daemon=True); ta.start()
tbs = [threading.Thread(target=fetcher, daemon=True) for _ in range(NF)]
for t in tbs: t.start()
ta.join()
for _ in range(NF): q.put(None)
for t in tbs: t.join()
print("DONE")
