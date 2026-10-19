#!/usr/bin/env python3
"""Fetch arXiv HTML for a list of papers and extract (a) Limitation / Future Work /
Discussion sections and (b) author affiliations, flagging papers led by
US / European groups.

  python3 scripts/harvest_arxiv.py cands.json out.jsonl
"""
import json, re, sys, time, threading, queue
from pathlib import Path
import requests
from bs4 import BeautifulSoup

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
UA = {"User-Agent": "awesome-research-ideas-harvester/0.3 (mailto:mu.chen@mbzuai.ac.ae)"}
SEC_RE = re.compile(r"(limitation|future (work|direction|research)|discussion|conclusion|open (problem|question)|broader impact|failure)", re.I)
WEST = re.compile(r"Stanford|Berkeley|Carnegie Mellon|\bCMU\b|Massachusetts Institute|\bMIT\b|Harvard|Princeton|Yale|Cornell|Columbia University|New York University|\bNYU\b|University of Washington|UCLA|UC San Diego|UCSD|Illinois|Michigan|Wisconsin|UT Austin|University of Texas|Georgia (Institute of )?Tech|Johns Hopkins|University of Pennsylvania|UPenn|Duke|Brown University|Caltech|Southern California|\bUSC\b|Maryland|Purdue|Northeastern|UMass|Amherst|Toronto|Waterloo|McGill|Mila|Montr[eé]al|British Columbia|Alberta|Vector Institute|Oxford|Cambridge|Imperial College|University College London|\bUCL\b|Edinburgh|ETH|EPFL|Technical University of Munich|\bTUM\b|LMU|Max Planck|Saarland|Amsterdam|Delft|KU Leuven|INRIA|Inria|Sorbonne|PSL|Copenhagen|KTH|T[uü]bingen|Heidelberg|Darmstadt|Zurich|Z[uü]rich|Google|DeepMind|\bMeta\b|FAIR|Microsoft|OpenAI|Anthropic|NVIDIA|Allen Institute|\bAI2\b|Apple|IBM|Amazon|Salesforce|Adobe|Hugging ?Face|Databricks|Princeton|Rice University|Virginia|Ohio State|Washington University|Chicago|Boston University|Dartmouth|Weizmann|Technion|Tel Aviv|Hebrew University|G[oö]ttingen|Bonn|Freiburg|Stuttgart|Mannheim|Hamburg|Berlin|Aachen|Karlsruhe|KIT\b|Wien|Vienna|Graz|Lausanne|Geneva|Bern\b|Basel|Utrecht|Groningen|Leiden|Ghent|Lisbon|Madrid|Barcelona|Pompeu|Politecnico|Bocconi|Sapienza|Pisa|Trento|Torino|Turin|Helsinki|Aalto|Oslo|Stockholm|Chalmers|Uppsala|Aarhus|Warsaw|Prague|Dublin|Trinity College|Manchester|Bristol|Glasgow|Sheffield|King's College|Warwick|Southampton|Queen Mary|Paris|Saclay|ENS\b|Polytechnique|Grenoble|Lyon|Naver Labs Europe|Mistral|Aleph Alpha|Cohere|Bosch|Siemens|IST Austria|ELLIS|Northwestern|Notre Dame|Emory|Vanderbilt|Utah|Arizona|Colorado|Minnesota|Rutgers|Stony Brook|UC Davis|UC Irvine|Santa Barbara|Santa Cruz|Riverside|Virginia Tech|NC State|Penn State|Pittsburgh|Rochester|TTIC|Toyota Technological|Scale AI|Together AI|ServiceNow|Intel|Qualcomm|Snap\b|Bloomberg|JPMorgan|Morgan Stanley|Netflix|Uber|LinkedIn|Spotify", re.I)
EAST = re.compile(r"Tsinghua|Peking|Zhejiang|Shanghai|Fudan|Nanjing|Wuhan|Sun Yat-sen|Harbin|Beihang|Renmin|USTC|University of Science and Technology of China|Chinese Academy|\bCAS\b|Alibaba|Tencent|ByteDance|Baidu|Huawei|SenseTime|Xiaomi|Kuaishou|JD|Ant Group|Meituan|KAIST|Seoul|Yonsei|Tokyo|Kyoto|NUS|National University of Singapore|Nanyang|NTU|HKUST|Hong Kong|CUHK|HKU|Macau|Zhipu|Moonshot|DeepSeek|Westlake|Shenzhen|Xi'an|Tianjin|Sichuan|Southeast University|Xiamen|Shandong|Jilin|Dalian|MBZUAI", re.I)

done = set()
if OUT.exists():
    for l in OUT.read_text().splitlines():
        try: done.add(json.loads(l)["arxiv"])
        except Exception: pass
lock = threading.Lock()
def emit(r):
    with lock:
        with OUT.open("a") as f: f.write(json.dumps(r, ensure_ascii=False) + "\n")

def parse(html):
    soup = BeautifulSoup(html, "lxml"); out = {}
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
    au = soup.select_one(".ltx_authors")
    aff = au.get_text(" ", strip=True)[:2500] if au else ""
    ab = soup.select_one("div.ltx_abstract")
    return out, aff, (ab.get_text(" ", strip=True)[:1500] if ab else "")

q = queue.Queue()
for c in json.loads(SRC.read_text()):
    if c["arxiv"] not in done: q.put(c)
def worker():
    while True:
        try: c = q.get_nowait()
        except queue.Empty: return
        time.sleep(1.5)
        secs, aff, ab, how = {}, "", "", "none"
        try:
            r = requests.get(f"https://arxiv.org/html/{c['arxiv']}", headers=UA, timeout=60)
            if r.status_code == 200 and "ltx_document" in r.text:
                secs, aff, ab = parse(r.text); how = "arxiv-html"
        except Exception: pass
        w, e = len(set(m.lower() for m in WEST.findall(aff))), len(set(m.lower() for m in EAST.findall(aff)))
        c.update(sections=secs, affiliations=aff[:2500], abstract=c.get("abstract") or ab, fulltext=how, west=w, east=e, western=bool(w and w >= e))
        emit(c); print(f"{how:10s} W{w}/E{e} secs={len(secs)} {c['title'][:70]}", flush=True)
ts = [threading.Thread(target=worker) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("DONE")
