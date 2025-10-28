# NMLR Baseline (CoT vs NMLR)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/mfifth/nmlr/workflows/CI/badge.svg)](https://github.com/mfifth/nmlr/actions)

**NMLR (Networked Multi-Layered Reasoning)** is a framework for improving LLM reasoning reliability.
Instead of relying on a *single* chain of thought, NMLR generates **multiple candidate reasoning paths**, evaluates them with **verifiers**, and selects the solution that best satisfies formal or heuristic correctness checks.

Where **Chain-of-Thought (CoT)** commits early and hopes the reasoning is correct, **NMLR treats reasoning as a search problem**, guided by verification.

---

## What Problem Does NMLR Solve?

LLMs often produce answers that *sound* correct but are wrong (hallucinations, logical slips, hidden assumption jumps). This happens because:

* CoT is **single-path** (one reasoning path, no backtracking)
* Models tend to **rationalize** instead of **reason**
* There is no internal consistency check before output

NMLR fixes this by:

| Step | NMLR Component                                      | Purpose                                       |
| ---- | --------------------------------------------------- | --------------------------------------------- |
| 1    | Generate multiple reasoning candidates              | Avoids committing to a single path            |
| 2    | Verify each path using deterministic/verifier rules | Detects invalid reasoning                     |
| 3    | Score and rank surviving solutions                  | Selects the most correct, not the most fluent |
| 4    | Optionally refine reasoning iteratively             | Improves clarity and stability                |

This turns reasoning into a **search-and-check** process rather than a one-shot guess.

---

## How It Works (High-Level Diagram)

```
        ┌──────────────┐
        │   Problem    │
        └──────┬───────┘
               │
      Generate Reasoning Candidates
               │
     ┌─────────┴─────────┐
     │   Candidate 1     │
     │   Candidate 2     │
     │   Candidate 3     │   ...
     └─────────┬─────────┘
               │
        Run Verifiers (rules / tests)
               │
     ┌─────────┴─────────┐
     │   Filter invalid   │  ← hallucinations / logic errors get removed
     └─────────┬─────────┘
               │
         Score & Select Best
               │
        ┌──────┴──────┐
        │   Answer     │
        └──────────────┘
```

This mirrors how humans solve complex problems:
**try → check → refine**, not simply "think once and declare."

---

## Quick Results

After running experiments (`make all`), you'll see:

![Accuracy by Method](runs/accuracy_by_method.png)

NMLR **outperforms** CoT and self-consistency CoT on ambiguous logic tasks by exploring reasoning space more fully and enforcing correctness checks.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)
- API keys for cloud providers (optional - Ollama works locally)

### 1. Setup Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### (Optional) Dev Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

### 2. Configure LLM Provider

In `.env`:

| Provider       | Example Model       | Notes                       |
| -------------- | ------------------- | --------------------------- |
| Ollama (local) | `llama3.2`          | No API cost                 |
| OpenAI         | `gpt-4o-mini`       | Best reasoning stability    |
| Anthropic      | `claude-3-5-sonnet` | Strong verifier consistency |
| xAI            | `grok-beta`         | Good multi-path exploration |
| Google Gemini  | `gemini-1.5-pro`    | Strong structured reasoning |

### 3. Run Experiments

```bash
make run-cot
make run-cot-sc
make run-nmlr
make eval
make plot
make all
```

### 4. View Results

* All experiment outputs saved in `runs/`
* `summary.csv` shows exact-match accuracy
* `accuracy_by_method.png` shows comparison chart (generated after `make plot`)
* `token_log.csv` tracks API usage

---

## Live Demo

### Local Gradio Demo

```bash
pip install -r demo/requirements.txt
make demo
```

Then open the web UI to interactively explore NMLR.

---

## Costs & Logging

```bash
make costs
```

See `costs.py` to customize provider rate assumptions.

---

## Cite This Work

```
@software{nmlr2025,
  title={Networked Multi-Layered Reasoning (NMLR)},
  author={Quinto, Matt and ChatGPT Assistant},
  year={2025},
  url={https://github.com/mfifth/nmlr}
}
```

---

## API Documentation

### Core Classes

- **`nmlr.search.nmlr_search()`**: Main search function that generates, verifies, and scores reasoning candidates
- **`nmlr.scoring.LLMEvaluator`**: LLM-based scoring with rubric evaluation
- **`nmlr.scoring.blended_scorer()`**: Combines LLM scores with heuristic penalties
- **`nmlr.verifier.*`**: Verification classes (`NonEmptyAnswer`, `NoContradiction`, `AlwaysTrue`)
- **`nmlr.llm_adapters.*`**: Provider classes (`OpenAIClient`, `AnthropicClient`, `GeminiClient`)

### Configuration

Environment variables:
- `NMLR_PROVIDER`: LLM provider (ollama, openai, anthropic, xai, gemini)
- `NMLR_MODEL`: Model name
- Provider-specific API keys (OPENAI_API_KEY, etc.)

---

## Project Structure

```
nmlr/                      # Core engine
├── __init__.py           # Package exports
├── candidate.py          # Candidate reasoning class
├── llm_adapters.py       # LLM provider integrations
├── scoring.py            # Scoring and evaluation
├── search.py             # Main NMLR search algorithm
└── verifier.py           # Verification rules

experiments/ambiguous_logic/  # Benchmark tasks
├── data.jsonl            # Test cases
├── run_baseline_cot.py   # CoT baseline
├── run_baseline_cot_sc.py # Self-consistency CoT
├── run_nmlr.py           # NMLR implementation
├── metrics.py            # Evaluation scripts
└── costs.py              # Cost analysis

tests/                    # Unit tests
demo/                     # Web demo interface
├── app.py                # Gradio application
└── requirements.txt      # Demo dependencies

docs/                     # Documentation
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # Development guide
├── CODE_OF_CONDUCT.md    # Community standards
├── SECURITY.md           # Security policy
└── RELEASE_CHECKLIST.md  # Release process

.github/                  # CI/CD workflows
notebooks/                # Research walkthroughs
runs/                     # Experiment outputs
```

---

## Costs & Logging

```bash
make costs
```

See `experiments/ambiguous_logic/costs.py` to customize provider rate assumptions.

---

## Troubleshooting

### Common Issues

- **API quota errors**: Switch to Ollama local provider (`NMLR_PROVIDER=ollama`)
- **Import errors**: Ensure `pip install -e .` after cloning
- **Test failures**: Check Python version (3.11+ required)
- **Model not found**: Verify model name and provider configuration
- **Demo won't start**: Install demo requirements with `pip install -r demo/requirements.txt`

### Prerequisites

- Python 3.11+
- Virtual environment recommended
- API keys for cloud providers (optional, Ollama works locally)
```

---

## Project Structure

```
nmlr/                      # Core engine
experiments/ambiguous_logic # Benchmark tasks
tests/                     # Unit tests
notebooks/                 # Research walkthroughs
demo/                      # Web demo interface
```
