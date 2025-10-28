import pytest
from unittest.mock import Mock, patch
from nmlr.candidate import Candidate
from nmlr.search import nmlr_search
from nmlr.verifier import NonEmptyAnswer
from nmlr.scoring import blended_scorer

@patch('nmlr.scoring.get_llm')
def test_integration_nmlr_pipeline(mock_get_llm):
    # Mock LLM for scoring
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.text = '{"score": 0.7, "reason": "Mock reason"}'
    mock_llm.complete.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    # Mock expand function
    def mock_expand(state):
        return [("Mock answer 1", 0.1), ("Mock answer 2", 0.2)]
    
    verifiers = [NonEmptyAnswer()]
    
    initial = Candidate(state="")
    results = nmlr_search(initial, "test task", mock_expand, verifiers, 
                         lambda t, s: blended_scorer(t, s, lambda task, cand: (0.8, "reason")), 
                         max_steps=1, beam_size=2)
    
    assert len(results) == 2
    assert all(isinstance(c, Candidate) for c in results)
    # Results are sorted by score descending
