import pytest
from unittest.mock import Mock, patch, MagicMock
from nmlr.llm_adapters import get_llm, OpenAIClient, AnthropicClient, GeminiClient

@patch('openai.OpenAI')
def test_get_llm_openai(mock_openai):
    mock_client = Mock()
    mock_openai.return_value = mock_client
    llm = get_llm(provider="openai", model="test-model")
    assert isinstance(llm, OpenAIClient)
    mock_openai.assert_called_once()

@patch('anthropic.Anthropic')
def test_get_llm_anthropic(mock_anthropic):
    mock_client = Mock()
    mock_anthropic.return_value = mock_client
    llm = get_llm(provider="anthropic", model="test-model")
    assert isinstance(llm, AnthropicClient)

@patch('google.generativeai.GenerativeModel')
def test_get_llm_gemini(mock_genai):
    mock_client = Mock()
    mock_genai.return_value = mock_client
    llm = get_llm(provider="gemini", model="test-model")
    assert isinstance(llm, GeminiClient)

def test_get_llm_invalid_provider():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm(provider="invalid")

@patch('openai.OpenAI')
@patch('nmlr.llm_adapters._append_token_log')
def test_openai_complete(mock_log, mock_openai):
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    llm = OpenAIClient(model="gpt-4o-mini")
    result = llm.complete("prompt", "system")
    
    assert result.text == "Test response"
    assert result.token_usage == {"input": 10, "output": 5}
    mock_log.assert_called_once_with("openai", "gpt-4o-mini", {"input": 10, "output": 5})
