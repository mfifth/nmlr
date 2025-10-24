# NMLR Baseline (CoT vs NMLR)
Compare single-path Chain-of-Thought vs verifier-driven NMLR with an LLM scoring layer.

## Quick Start

### 1. Setup Environment
```bash
python -m venv .venv && source .venv/bin/activate   # macOS/Linux
# or on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Choose LLM Provider
Edit `.env` to set `NMLR_PROVIDER` and add API keys if needed:

- **Ollama (free, local)**: `NMLR_PROVIDER=ollama`, `NMLR_MODEL=llama3.2`
  - Install Ollama: https://ollama.ai/download
  - Run: `ollama pull llama3.2 && ollama serve`

- **OpenAI**: `NMLR_PROVIDER=openai`, `NMLR_MODEL=gpt-4o-mini`
  - Add `OPENAI_API_KEY=sk-...` (requires billing: https://platform.openai.com/account/billing)

- **Anthropic**: `NMLR_PROVIDER=anthropic`, `NMLR_MODEL=claude-3-5-sonnet-latest`
  - Add `ANTHROPIC_API_KEY=sk-ant-...`

- **xAI (Grok)**: `NMLR_PROVIDER=xai`, `NMLR_MODEL=grok-beta`
  - Add `XAI_API_KEY=xai-...`

- **Google Gemini**: `NMLR_PROVIDER=gemini`, `NMLR_MODEL=gemini-1.0-pro`
  - Add `GOOGLE_API_KEY=...`

### 3. Run Experiments
```bash
# Run CoT baseline
make run-cot

# Run self-consistency CoT
make run-cot-sc

# Run NMLR
make run-nmlr

# Compute metrics (update paths in Makefile if needed)
make eval

# Plot results
make plot

# Check costs
make costs

# Run all
make all
```

### 4. View Results
- Results saved in `runs/` with timestamps
- `summary.csv`: accuracy comparison
- `accuracy_by_method.png`: bar chart
- `results_table.tex`: LaTeX table
- `token_log.csv`: API usage

## Project Structure
- `nmlr/`: Core library
- `experiments/ambiguous_logic/`: Benchmark on logic puzzles
- `tests/`: Unit tests
- `notebooks/`: Exploration notebook

## Citation
If you use this work, please cite:
```
@software{nmlr2025,
  title={Networked Multi-Layered Reasoning (NMLR)},
  author={Quinto, Matt and ChatGPT Assistant},
  year={2025},
  url={https://github.com/your-org/nmlr}
}
```
