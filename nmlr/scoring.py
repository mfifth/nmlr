from typing import Callable, Optional, Tuple
from .llm_adapters import get_llm

Score = float
Reason = str

class LLMEvaluator:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None,
                 rubric: Optional[str] = None):
        self.llm = get_llm(provider=provider, model=model)
        self.rubric = rubric or (
            "You are a verifier. Score the candidate's hypothesis for correctness "
            "given the task. Return a single JSON object: "
            '{"score": number between 0 and 1, "reason": "short justification"}'
        )

    def __call__(self, task: str, candidate_state: str) -> Tuple[Score, Reason]:
        prompt = f"""Task:
{task}

Candidate:
{candidate_state}

{self.rubric}"""
        resp = self.llm.complete(prompt, system="Act as a strict verifier.")
        text = resp.text.strip()
        import json, re
        try:
            obj = json.loads(text)
        except Exception:
            m = re.search(r'\\{.*\\}', text, re.S)
            obj = json.loads(m.group(0)) if m else {"score": 0.0, "reason": "unparseable"}
        score = float(obj.get("score", 0.0))
        reason = str(obj.get("reason", ""))
        score = max(0.0, min(1.0, score))
        return score, reason

def heuristic_len_penalty(candidate_state: str) -> float:
    return max(0.0, 1.0 - (len(candidate_state) / 500.0))

def blended_scorer(task: str, candidate_state: str,
                   llm_eval: Callable[[str,str], Tuple[Score,Reason]]) -> Tuple[Score,Reason]:
    llm_score, reason = llm_eval(task, candidate_state)
    h = heuristic_len_penalty(candidate_state)
    final = 0.9 * llm_score + 0.1 * h
    return final, reason
