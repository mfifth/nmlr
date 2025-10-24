from typing import Callable, Iterable, List, Tuple
from .candidate import Candidate

ExpandFn = Callable[[str], Iterable[Tuple[str, float]]]
VerifierFn = Callable[[Candidate], bool]
ScorerFn = Callable[[str, str], Tuple[float, str]]  # (score, reason)

def nmlr_search(initial: Candidate,
                task: str,
                expand_fn: ExpandFn,
                verifiers: List[VerifierFn],
                scorer: ScorerFn,
                max_steps: int = 8,
                beam_size: int = 8) -> List[Candidate]:
    frontier = [initial]
    results: List[Candidate] = []

    for _ in range(max_steps):
        new_frontier: List[Candidate] = []
        for cand in frontier:
            for new_state, local_bonus in expand_fn(cand.state):
                child = cand.extend(new_state, 0.0)
                if all(v.check(child) for v in verifiers):
                    s, _ = scorer(task, child.state)
                    child.score = s + local_bonus
                    new_frontier.append(child)

        if not new_frontier:
            break

        new_frontier.sort(key=lambda c: -c.score)
        frontier = new_frontier[:beam_size]
        results.extend(frontier)

    return results
