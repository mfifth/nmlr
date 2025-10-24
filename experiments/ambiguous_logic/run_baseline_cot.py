import json, os, argparse, time
from tqdm import tqdm
from nmlr.llm_adapters import get_llm

def ask_cot(llm, prompt: str) -> str:
    sys = "Reason step-by-step. Then provide a final answer after the word 'Answer:'."
    resp = llm.complete(prompt, system=sys).text
    ans = resp.split("Answer:")[-1].strip() if "Answer:" in resp else resp.strip()
    return ans[:200]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", type=str, default=None)
    ap.add_argument("--model", type=str, default=None)
    ap.add_argument("--runs-dir", type=str, default="runs")
    args = ap.parse_args()

    llm = get_llm(provider=args.provider, model=args.model)
    rows = []
    base = os.path.dirname(__file__)
    data = os.path.join(base, "data.jsonl")

    os.makedirs(args.runs_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.runs_dir, f"cot_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    with open(data) as f:
        for line in tqdm(f):
            ex = json.loads(line)
            out = ask_cot(llm, ex["prompt"])
            rows.append({"id": ex["id"], "pred": out, "gold": ex["gold"]})

    outp = os.path.join(out_dir, "baseline_results.jsonl")
    with open(outp, "w") as w:
        for r in rows: w.write(json.dumps(r) + "\n")

    import json as _json
    with open(os.path.join(out_dir, "config.json"), "w") as w:
        _json.dump({"method":"cot","provider":args.provider,"model":args.model}, w, indent=2)

    print(f"Wrote {outp}")

if __name__ == "__main__":
    main()
