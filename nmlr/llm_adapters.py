import os
from dataclasses import dataclass
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMResponse:
    text: str
    token_usage: Optional[dict] = None

class LLM:
    def complete(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        raise NotImplementedError

class OpenAIClient(LLM):
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key_env: Optional[str] = "OPENAI_API_KEY", provider: str = "openai"):
        from openai import OpenAI
        api_key = "" if api_key_env is None else os.getenv(api_key_env, "")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model or os.getenv("NMLR_MODEL", "gpt-4o-mini")
        self.provider = provider

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def complete(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=self.model, messages=msgs)
        text = resp.choices[0].message.content
        usage = {"input": getattr(resp.usage, "prompt_tokens", None),
                 "output": getattr(resp.usage, "completion_tokens", None)}
        _append_token_log(self.provider, self.model, usage)
        return LLMResponse(text=text, token_usage=usage)

class AnthropicClient(LLM):
    def __init__(self, model: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model or os.getenv("NMLR_MODEL", "claude-3-5-sonnet-latest")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def complete(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        msgs = [{"role": "user", "content": prompt}]
        resp = self.client.messages.create(
            model=self.model,
            system=system or "",
            max_tokens=512,
            messages=msgs,
        )
        # Anthropics' responses are blocks with text attributes.
        text = "".join([getattr(blk, "text", "") for blk in resp.content])
        usage = {"input": getattr(resp.usage, "input_tokens", None),
                 "output": getattr(resp.usage, "output_tokens", None)}
        _append_token_log("anthropic", self.model, usage)
        return LLMResponse(text=text, token_usage=usage)

class GeminiClient(LLM):
    def __init__(self, model: Optional[str] = None):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = model or os.getenv("NMLR_MODEL", "gemini-1.0-pro")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def complete(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        import google.generativeai as genai
        client = genai.GenerativeModel(self.model)
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        resp = client.generate_content(full_prompt)
        text = resp.text
        usage = {"input": getattr(resp, "usage_metadata", {}).get("prompt_token_count"), "output": getattr(resp, "usage_metadata", {}).get("candidates_token_count")}
        _append_token_log("gemini", self.model, usage)
        return LLMResponse(text=text, token_usage=usage)

def get_llm(provider: Optional[str] = None, model: Optional[str] = None) -> LLM:
    provider = (provider or os.getenv("NMLR_PROVIDER", "openai")).lower()
    if provider == "openai":
        return OpenAIClient(model=model)
    if provider == "anthropic":
        return AnthropicClient(model=model)
    if provider == "xai":
        return OpenAIClient(model=model or "grok-beta", base_url="https://api.x.ai/v1", api_key_env="XAI_API_KEY", provider="xai")
    if provider == "gemini":
        return GeminiClient(model=model)
    if provider == "ollama":
        return OpenAIClient(model=model or "llama3.2", base_url="http://localhost:11434/v1", api_key_env=None, provider="ollama")
    raise ValueError(f"Unknown LLM provider: {provider}")

def _append_token_log(provider_name: str, model: str, usage: dict):
    try:
        import os, csv, time
        os.makedirs("runs", exist_ok=True)
        with open("runs/token_log.csv", "a", newline="") as f:
            w = csv.writer(f)
            w.writerow([int(time.time()), provider_name, model, usage.get("input"), usage.get("output")])
    except Exception:
        pass
