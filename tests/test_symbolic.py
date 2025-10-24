from nmlr.candidate import Candidate

def test_extend():
    c = Candidate("a", score=1.0)
    d = c.extend("b", 0.5)
    assert d.state == "b"
    assert d.score == 1.5
    assert c.state in d.history

def test_history_list():
    c = Candidate("x")
    d = c.extend("y", 0.0)
    assert isinstance(d.history, list)
