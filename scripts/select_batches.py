#!/usr/bin/env python3
"""Classify harvested papers into categories and build writing batches.

  python3 scripts/select_batches.py data/papers.jsonl data/batches
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict, Counter

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)

CATS = [  # (id, name, regex over title+abstract)
 ("04-multi-agent-systems",   "🤝 Multi-Agent Systems & LLM Agents", r"multi-?agent|agentic|\bagents?\b|tool[- ]use|workflow|web ?agent|swe-?bench|computer[- ]use|collaborat"),
 ("05-embodied-robotics",     "🤖 Embodied AI & Robotics", r"robot|manipulat|locomot|embodied|navigation|vision-language-action|\bVLA\b|policy learning|imitation|teleoperat|sim-to-real|humanoid|grasp"),
 ("03-diffusion-generative",  "🌊 Diffusion & Generative Models", r"diffusion|flow[- ]matching|score[- ]based|generative model|text-to-(image|video|3d)|image generation|video generation|autoregressive (image|visual)|rectified flow|consistency model|masked diffusion|\bVAE\b|GAN\b"),
 ("02-alignment-safety",      "🛡️ Alignment, Safety & Interpretability", r"alignment|safety|jailbreak|refus|RLHF|\bDPO\b|preference|reward model|interpretab|mechanistic|sparse autoencoder|unlearning|watermark|privacy|membership inference|bias|fairness|hallucinat|model editing|red[- ]team|adversarial"),
 ("01-llm-reasoning-rl",      "🧠 LLM Reasoning & RL Post-Training", r"reasoning|chain[- ]of[- ]thought|\bRLVR\b|\bGRPO\b|math|theorem|code generation|self-improv|test-time|inference[- ]time (scaling|compute)|verif|process reward|in-context learning|planning"),
 ("08-architecture-efficiency","⚙️ Architecture, Efficiency & Scaling", r"attention|transformer|state[- ]space|\bmamba\b|mixture[- ]of[- ]experts|\bMoE\b|KV[- ]cache|quantiz|pruning|distillation|scaling law|long[- ]context|tokeniz|optimizer|pretrain|sparsity|efficient|speculative|throughput|compression"),
 ("07-multimodal-vlm",        "🖼️ Multimodal & Vision-Language Models", r"vision[- ]language|multimodal|\bVLM\b|\bMLLM\b|visual question|image caption|CLIP|video understanding|audio|speech|any-to-any|omni"),
 ("06-vision-3d",             "👁️ Computer Vision & 3D", r"3d|gaussian splatting|\bNeRF\b|point cloud|segmentation|detection|depth|pose|reconstruction|camera|rendering|\bSLAM\b|optical flow|video|image|visual|scene|mesh|tracking|photometric|neural radiance"),
 ("09-nlp-language",          "🗣️ NLP & Language", r"language model|\bLLM|translation|multilingual|retrieval|RAG\b|question answering|summariz|dialogue|linguistic|grammar|tokens?\b|corpus|benchmark|evaluation|annotation"),
 ("10-theory-optimization",   "📐 Theory, Optimization & Learning", r"theor|bound|convergence|generalization|optimization|sample complexity|bandit|online learning|causal|kernel|Bayesian|variational|probabilistic|estimation|statistic|PAC|regret|minimax|graph neural|GNN|equivarian|geometric"),
 ("11-ai4science-other",      "🔬 AI for Science & Others", r"protein|molecul|drug|chemistry|physics|climate|weather|biolog|genom|medical|clinical|material|PDE|simulation|neuroscience|brain|time[- ]series|tabular|recommend|federated|reinforcement learning"),
]
SEC_PRIORITY = re.compile(r"limitation|future|open problem|open question|failure", re.I)

def classify(r):
    text = " ".join([r["title"], r.get("abstract") or "", " ".join(list(r.get("sections", {}).keys()))])
    scores = {}
    for cid, name, rx in CATS:
        n = len(re.findall(rx, text, re.I)); n_title = len(re.findall(rx, r["title"], re.I))
        scores[cid] = n + 3 * n_title
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "11-ai4science-other"

def gap_quality(r):
    secs = r.get("sections", {})
    if not secs: return 0
    score = 0
    for h, t in secs.items():
        w = 3 if SEC_PRIORITY.search(h) else 1
        score += w * min(len(t), 3000) / 1000
    return score

tier = {"award": 3, "award-candidate": 3, "oral": 1}
rows = [json.loads(l) for l in SRC.read_text().splitlines()]
rows = [r for r in rows if not r.get("dropped") and r.get("arxiv")]
for r in rows:
    r["category"] = classify(r); r["gap_q"] = gap_quality(r)
    r["priority"] = tier.get(r["track"], 1) * 2 + r["gap_q"] + (0.5 if r["year"] >= 2025 else 0)
by = defaultdict(list)
for r in rows:
    if r["gap_q"] > 0.3: by[r["category"]].append(r)
summary = {}
for cid, name, _ in CATS:
    lst = sorted(by.get(cid, []), key=lambda r: -r["priority"])
    summary[cid] = len(lst)
    (OUT / f"{cid}.json").write_text(json.dumps(dict(category=cid, name=name, papers=[
        dict(title=r["title"], venue=r["venue"], year=r["year"], track=r["track"], arxiv=r["arxiv"], authors=r.get("authors",""),
             abstract=(r.get("abstract") or "")[:1200], sections={k: v[:2500] for k, v in r["sections"].items()}, priority=round(r["priority"],2))
        for r in lst]), ensure_ascii=False, indent=1))
print("with arXiv:", len(rows), "with usable gap sections:", sum(summary.values()))
for cid, n in summary.items(): print(f"  {cid:28s} {n}")
print("fulltext:", Counter(r.get("fulltext") for r in rows))
