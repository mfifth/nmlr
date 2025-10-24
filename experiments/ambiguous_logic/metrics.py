import json, os, argparse, pandas as pd

def normalize(x: str) -> str:
    return (x or "").strip().lower()

def load(path):
    rows = []
    with open(path) as f:
        for ln in f:
            rows.append(json.loads(ln))
    return rows

def exact_match(pred: str, gold: str) -> int:
    return int(normalize(pred).startswith(normalize(gold)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cot", type=str, required=True, help="path to baseline_results.jsonl or baseline_sc_results.jsonl")
    ap.add_argument("--nmlr", type=str, required=True, help="path to nmlr_results.jsonl")
    ap.add_argument("--out-dir", type=str, required=True, help="where to write summary.csv")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    frames = []
    gold_map = {}

    for name, path in {"cot": args.cot, "nmlr": args.nmlr}.items():
        rows = load(path)
        if not gold_map:
            gold_map = {r["id"]: r["gold"] for r in rows}
        acc = []
        for r in rows:
            em = exact_match(r["pred"], gold_map[r["id"]])
            acc.append({"id": r["id"], "method": name, "em": em})
        frames.append(pd.DataFrame(acc))

    df = pd.concat(frames)
    pivot = df.groupby("method")["em"].mean().reset_index().rename(columns={"em":"exact_match"})
    pivot.to_csv(os.path.join(args.out_dir, "summary.csv"), index=False)
    print(pivot)

if __name__ == "__main__":
    main()
