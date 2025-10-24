import csv, os, argparse, pandas as pd

PRICES = {
    # Example placeholder CPM ($ per 1K tokens) — adjust to your actual rates.
    ("openai","gpt-4o-mini","input"): 0.150,
    ("openai","gpt-4o-mini","output"): 0.600,
    ("anthropic","claude-3-5-sonnet-latest","input"): 3.00,
    ("anthropic","claude-3-5-sonnet-latest","output"): 15.00,
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-log", type=str, default="runs/token_log.csv")
    args = ap.parse_args()
    if not os.path.exists(args.token_log):
        print("No token log found.")
        return
    rows = []
    with open(args.token_log) as f:
        r = csv.reader(f)
        for ts, provider, model, inp, out in r:
            rows.append({"provider":provider, "model":model,
                         "input": int(inp) if inp not in (None,"","None") else 0,
                         "output": int(out) if out not in (None,"","None") else 0})
    df = pd.DataFrame(rows)
    agg = df.groupby(["provider","model"]).sum(numeric_only=True).reset_index()
    def cost_row(p, m, inp, out):
        cin = PRICES.get((p,m,"input"), 0.0) * (inp/1000.0)
        cout = PRICES.get((p,m,"output"), 0.0) * (out/1000.0)
        return cin + cout
    agg["cost_usd_est"] = agg.apply(lambda r: cost_row(r["provider"], r["model"], r["input"], r["output"]), axis=1)
    print(agg)

if __name__ == "__main__":
    main()
