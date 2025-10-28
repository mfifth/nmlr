from nmlr.candidate import Candidate
from nmlr.verifier import NonEmptyAnswer, NoContradiction, AlwaysTrue

def test_non_empty():
    v = NonEmptyAnswer()
    assert v.check(Candidate("ok"))
    assert not v.check(Candidate(""))

def test_no_contradiction():
    v = NoContradiction()
    assert v.check(Candidate("fine"))
    assert not v.check(Candidate("This is a contradiction."))

def test_always_true():
    v = AlwaysTrue()
    assert v.check(Candidate("anything"))
    assert v.check(Candidate(""))
