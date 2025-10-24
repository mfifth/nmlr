import json, os, argparse, time
from tqdm import tqdm
from nmlr.candidate import Candidate
from nmlr.search import nmlr_search
from nmlr.verifier import NonEmptyAnswer, NoContradiction, Verifier
from nmlr.scoring import LLMEvaluator, blended_scorer
from nmlr.llm_adapters import get_llm
import random

def expand_fn_factory(llm, seed=None):
    rng = random.Random(seed)
    def expand_fn(state: str):
        base = state or ""
        prompt = (
            "Propose up to 3 short ALTERNATIVE answers (distinct), each on its own line, "
            "without preamble. Keep each under 20 words. Current guess:\n"
            f"{base}"
        )
        resp = llm.complete(prompt, system="Generate alternatives only. No explanations.")
        lines = [ln.strip("- ").strip() for ln in resp.text.strip().splitlines() if ln.strip()]
        rng.shuffle(lines)
        return [(ln, 0.0) for ln in lines[:3]] or [("No Answer", -1.0)]
    return expand_fn

class AlwaysTrue(Verifier):
    def check(self, candidate) -> bool:
        return True

def solve_one(task: str, beam: int, steps: int, provider: str, model: str, use_verifiers: bool, seed: int):
    llm_gen = get_llm(provider=provider, model=model)
    expand_fn = expand_fn_factory(llm_gen, seed=seed)

    verifiers = [NonEmptyAnswer(), NoContradiction()] if use_verifiers else [AlwaysTrue()]

    llm_eval = LLMEvaluator(provider=provider, model=model)
    def scorer(task_txt, cand_state):
        return blended_scorer(task_txt, cand_state, llm_eval)

    initial = Candidate(state="")
    results = nmlr_search(initial, task, expand_fn, verifiers, scorer,
                          max_steps=steps, beam_size=beam)
    return results[0].state if results else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beam", type=int, default=6)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--no-verifiers", action="store_true", help="disable verifiers (use AlwaysTrue)")
    ap.add_argument("--provider", type=str, default=None)
    ap.add_argument("--model", type=str, default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--runs-dir", type=str, default="runs")
    args = ap.parse_args()

    random.seed(args.seed)

    base = os.path.dirname(__file__)
    inp = os.path.join(base, "data.jsonl")

    os.makedirs(args.runs_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tag = f"nmlr_b{args.beam}_s{args.steps}_{'nov' if args.no_verifiers else 'ver'}_{stamp}"
    out_dir = os.path.join(args.runs_dir, tag)
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    with open(inp) as f:
        for line in tqdm(f):
            ex = json.loads(line)
            pred = solve_one(
                ex["prompt"],
                beam=args.beam,
                steps=args.steps,
                provider=args.provider,
                model=args.model,
                use_verifiers=not args.no_verifiers,
                seed=args.seed
            )
            rows.append({"id": ex["id"], "pred": pred, "gold": ex["gold"]})

    outp = os.path.join(out_dir, "nmlr_results.jsonl")
    with open(outp, "w") as w:
        for r in rows: w.write(json.dumps(r) + "\n")

    import json as _json
    cfg = {
        "method": "nmlr",
        "beam": args.beam,
        "steps": args.steps,
        "use_verifiers": (not args.no_verifiers),
        "provider": args.provider,
        "model": args.model,
        "seed": args.seed
    }
    with open(os.path.join(out_dir, "config.json"), "w") as w:
        _json.dump(cfg, w, indent=2)

    print(f"Wrote {outp}")

if __name__ == "__main__":
    main()