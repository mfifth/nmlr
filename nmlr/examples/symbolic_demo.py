from nmlr.candidate import Candidate
from nmlr.search import nmlr_search
from nmlr.verifier import NonEmptyAnswer, NoContradiction
from nmlr.scoring import LLMEvaluator, blended_scorer
from nmlr.llm_adapters import get_llm

def expand_fn_factory(llm):
    def expand_fn(state: str):
        base = state or ""
        resp = llm.complete(
            f"Propose up to 3 short ALTERNATIVE answers, each on its own line, no preamble. Current guess: {base}",
            system="Generate alternatives only. No explanations."
        )
        lines = [ln.strip("- ").strip() for ln in resp.text.strip().splitlines() if ln.strip()]
        return [(ln, 0.0) for ln in lines[:3]] or [("No Answer", -1.0)]
    return expand_fn

def main():
    llm = get_llm()
    expand_fn = expand_fn_factory(llm)
    verifiers = [NonEmptyAnswer(), NoContradiction()]
    llm_eval = LLMEvaluator()
    def scorer(task_txt, cand_state):
        return blended_scorer(task_txt, cand_state, llm_eval)
    initial = Candidate(state="")
    res = nmlr_search(initial, "Say hello in one word.", expand_fn, verifiers, scorer, max_steps=2, beam_size=4)
    for r in res:
        print(r.state, r.score)

if __name__ == "__main__":
    main()
