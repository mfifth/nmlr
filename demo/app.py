import gradio as gr
from nmlr.candidate import Candidate
from nmlr.search import nmlr_search
from nmlr.verifier import NonEmptyAnswer, NoContradiction
from nmlr.scoring import LLMEvaluator, blended_scorer
from nmlr.llm_adapters import get_llm
import random

def expand_fn_factory(llm):
    def expand_fn(state: str):
        base = state or ""
        prompt = (
            "Propose up to 3 short ALTERNATIVE answers (distinct), each on its own line, "
            "without preamble. Keep each under 20 words. Current guess:\n"
            f"{base}"
        )
        resp = llm.complete(prompt, system="Generate alternatives only. No explanations.")
        lines = [ln.strip("- ").strip() for ln in resp.text.strip().splitlines() if ln.strip()]
        return [(ln, 0.0) for ln in lines[:3]] or [("No Answer", -1.0)]
    return expand_fn

def run_nmlr(task, beam, steps, provider, model):
    try:
        llm_gen = get_llm(provider=provider, model=model)
        expand_fn = expand_fn_factory(llm_gen)
        verifiers = [NonEmptyAnswer(), NoContradiction()]
        llm_eval = LLMEvaluator(provider=provider, model=model)
        scorer = lambda t, s: blended_scorer(t, s, llm_eval)
        initial = Candidate(state="")
        results = nmlr_search(initial, task, expand_fn, verifiers, scorer, max_steps=steps, beam_size=beam)
        top10 = results[:10]
        return "\n".join([f"{c.state}: {c.score:.3f}" for c in top10])
    except Exception as e:
        return f"Error: {str(e)}"

iface = gr.Interface(
    fn=run_nmlr,
    inputs=[
        gr.Textbox(label="Task", lines=3, placeholder="Enter a reasoning task, e.g., 'Solve 2+2'"),
        gr.Slider(2, 12, value=6, label="Beam Size"),
        gr.Slider(1, 6, value=4, label="Max Steps"),
        gr.Dropdown(["openai", "anthropic"], label="Provider"),
        gr.Textbox(label="Model", value="gpt-4o-mini")
    ],
    outputs=gr.Textbox(label="Top 10 Candidates"),
    title="NMLR Demo",
    description="Networked Multi-Layered Reasoning with LLM scoring."
)

if __name__ == "__main__":
    iface.launch()
