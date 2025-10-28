import pytest
from unittest.mock import Mock, patch
from nmlr.scoring import LLMEvaluator, blended_scorer, heuristic_len_penalty

@patch('nmlr.scoring.get_llm')
def test_llm_evaluator(mock_get_llm):
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.text = '{"score": 0.8, "reason": "Good"}'
    mock_llm.complete.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    evaluator = LLMEvaluator()
    score, reason = evaluator("task", "candidate")
    
    assert score == 0.8
    assert reason == "Good"
    mock_llm.complete.assert_called_once()

@patch('nmlr.scoring.get_llm')
def test_llm_evaluator_json_parse_error(mock_get_llm):
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.text = "Invalid JSON"
    mock_llm.complete.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    evaluator = LLMEvaluator()
    score, reason = evaluator("task", "candidate")
    
    assert score == 0.0  # Default on parse error
    assert reason == "unparseable"

def test_blended_scorer():
    mock_evaluator = Mock()
    mock_evaluator.return_value = (0.8, "reason")
    
    score, reason = blended_scorer("task", "short", mock_evaluator)
    
    # 0.9 * 0.8 + 0.1 * heuristic (len("short")=5, so 1.0 - 5/500 = 0.99)
    expected = 0.9 * 0.8 + 0.1 * 0.99
    assert score == pytest.approx(expected)
    assert reason == "reason"

def test_heuristic_len_penalty():
    assert heuristic_len_penalty("") == 1.0  # No penalty
    assert heuristic_len_penalty("short") == 0.99  # Slight penalty
    long_text = "a" * 600
    penalty = heuristic_len_penalty(long_text)
    assert penalty < 1.0  # Penalty applied
