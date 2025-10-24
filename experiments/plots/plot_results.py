import os, pandas as pd, matplotlib.pyplot as plt, argparse

def make_plot(df, out_dir):
    plt.figure()
    plt.bar(df["method"], df["exact_match"])
    plt.title("Exact Match Accuracy by Method")
    plt.xlabel("Method")
    plt.ylabel("Exact Match")
    plt.tight_layout()
    path = os.path.join(out_dir, "accuracy_by_method.png")
    plt.savefig(path, dpi=200)
    print(f"Wrote {path}")

def make_latex_table(df, out_dir):
    # Simple two-row latex table
    df2 = df.copy()
    df2["Exact Match (%)"] = (df2["exact_match"] * 100.0).round(1)
    cols = ["method", "Exact Match (%)"]
    latex = df2[cols].to_latex(index=False).replace("method", "Method")
    path = os.path.join(out_dir, "results_table.tex")
    with open(path, "w") as f:
        f.write(latex)
    print(f"Wrote {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=str, required=True, help="path to summary.csv")
    ap.add_argument("--out-dir", type=str, required=True)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.summary)
    make_plot(df, args.out_dir)
    make_latex_table(df, args.out_dir)

if __name__ == "__main__":
    main()
