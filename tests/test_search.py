import pytest
from unittest.mock import Mock, patch
from nmlr.search import nmlr_search
from nmlr.candidate import Candidate
from nmlr.verifier import NonEmptyAnswer, NoContradiction

def test_nmlr_search_basic():
    # Mock expand function: returns two candidates
    def mock_expand(state):
        return [("Answer A", 0.1), ("Answer B", 0.5)]
    
    # Mock verifiers: always pass
    verifiers = [NonEmptyAnswer(), NoContradiction()]
    
    # Mock scorer: returns score based on state
    def mock_scorer(task, state):
        return 0.8 if "A" in state or "B" in state else 0.5, "reason"
    
    initial = Candidate(state="")
    results = nmlr_search(initial, "test task", mock_expand, verifiers, mock_scorer, max_steps=1, beam_size=2)
    
    assert len(results) == 2
    assert results[0].state == "Answer A"  # Higher score: 0.8 + 0.1 = 0.9
    assert results[0].score == 0.9
    assert results[1].state == "Answer B"
    assert results[1].score == 1.3

def test_nmlr_search_with_pruning():
    def mock_expand(state):
        return [("Good", 0.0), ("Bad", 0.0)]
    
    verifiers = [NonEmptyAnswer()]  # NonEmptyAnswer fails on empty, but these are non-empty
    
    def mock_scorer(task, state):
        return 0.9 if "Good" in state else 0.1, "reason"
    
    initial = Candidate(state="")
    results = nmlr_search(initial, "test", mock_expand, verifiers, mock_scorer, max_steps=1, beam_size=1)
    
    assert len(results) == 1
    assert results[0].state == "Bad"

def test_nmlr_search_no_expansion():
    def mock_expand(state):
        return []  # No expansions
    
    verifiers = [NonEmptyAnswer()]
    def mock_scorer(task, state):
        return 0.5, "reason"
    
    initial = Candidate(state="")
    results = nmlr_search(initial, "test", mock_expand, verifiers, mock_scorer, max_steps=1, beam_size=1)
    
    assert len(results) == 0
