class Verifier:
    def check(self, candidate) -> bool:
        raise NotImplementedError

class NonEmptyAnswer(Verifier):
    def check(self, candidate) -> bool:
        return bool(str(candidate.state).strip())

class NoContradiction(Verifier):
    def check(self, candidate) -> bool:
        return "contradiction" not in str(candidate.state).lower()

class AlwaysTrue(Verifier):
    def check(self, candidate) -> bool:
        return True
