run-cot:
	python experiments/ambiguous_logic/run_baseline_cot.py --runs-dir runs

run-cot-sc:
	python experiments/ambiguous_logic/run_baseline_cot_sc.py --k 5 --runs-dir runs

run-nmlr:
	python experiments/ambiguous_logic/run_nmlr.py --beam 6 --steps 4 --runs-dir runs

eval:
	# Update the paths below to the most recent run dirs:
	python experiments/ambiguous_logic/metrics.py --cot runs/cot_*/baseline_results.jsonl --nmlr runs/nmlr_*/nmlr_results.jsonl --out-dir runs

plot:
	python experiments/plots/plot_results.py --summary runs/summary.csv --out-dir runs

costs:
	python experiments/ambiguous_logic/costs.py --token-log runs/token_log.csv

all: run-cot run-nmlr eval plot

demo:
	python demo/app.py

test:
	pytest --cov=nmlr --cov-report=term-missing
