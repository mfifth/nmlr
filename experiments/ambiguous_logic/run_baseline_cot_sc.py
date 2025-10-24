import json, os, statistics, argparse
from collections import Counter
from tqdm import tqdm
from nmlr.llm_adapters import get_llm

def ask_cot(llm, prompt: str) -> str:
    sys = "Reason step-by-step. Then provide a final answer after the word 'Answer:'."
    resp = llm.complete(prompt, system=sys).text
    return resp.split("Answer:")[-1].strip() if "Answer:" in resp else resp.strip()

def normalize(x: str) -> str:
    return (x or "").strip().lower()

def self_consistency_answers(llm, prompt: str, k: int):
    outs = [ask_cot(llm, prompt) for _ in range(k)]
    # choose modal (normalized) answer; break ties by shortest
    norm = [normalize(o) for o in outs]
    counts = Counter(norm)
    best_norm, _ = counts.most_common(1)[0]
    # pick a representative original string with that normalized form (prefer shortest)
    candidates = [o for o in outs if normalize(o) == best_norm]
    rep = min(candidates, key=len)
    return rep, outs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--provider", type=str, default=None)
    ap.add_argument("--model", type=str, default=None)
    ap.add_argument("--runs-dir", type=str, default="runs")
    args = ap.parse_args()

    llm = get_llm(provider=args.provider, model=args.model)
    base = os.path.dirname(__file__)
    data = os.path.join(base, "data.jsonl")

    os.makedirs(args.runs_dir, exist_ok=True)
    import time, json as _json
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.runs_dir, f"cot_sc_k{args.k}_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    with open(data) as f:
        for line in tqdm(f):
            ex = json.loads(line)
            pred, outs = self_consistency_answers(llm, ex["prompt"], args.k)
            rows.append({"id": ex["id"], "pred": pred, "gold": ex["gold"], "all": outs})

    outp = os.path.join(out_dir, "baseline_sc_results.jsonl")
    with open(outp, "w") as w:
        for r in rows: w.write(json.dumps(r) + "\n")

    cfg = {
        "method": "cot_self_consistency",
        "k": args.k,
        "provider": args.provider,
        "model": args.model,
    }
    with open(os.path.join(out_dir, "config.json"), "w") as w:
        _json.dump(cfg, w, indent=2)

    print(f"Wrote {outp}")

if __name__ == "__main__":
    main()
