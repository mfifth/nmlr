class Candidate:
    def __init__(self, state, score=0.0, history=None):
        self.state = state
        self.score = score
        self.history = history or []

    def extend(self, new_state, delta_score):
        return Candidate(
            state=new_state,
            score=self.score + delta_score,
            history=self.history + [self.state],
        )
