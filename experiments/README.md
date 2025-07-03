# Experiments

The experiments use [uv](https://docs.astral.sh/uv/).

install: `uv pip install -e .`

run: `uv run src/main.py`

```
resources/
├── prompts/
│   ├── improvement.yaml       # Prompt config for improvement experiments
│   ├── llm.yaml               # Prompt config for LLM-only experiments
│   ├── rag.yaml               # Prompt config for RAG experiments
│   └── shots.yaml             # Prompt config for few-shot experiments
│
├── results/
│   ├── improvement/           # output/metrics from improvement experiments
│   ├── llm/                   # output/metrics from LLM-only experiments
│   ├── rag/                   # output/metrics from RAG experiments
│   └── shots/                 # output/metrics from shot-based experiments
│
├── ground_truth_data.json     # JSON with annotated reference data
└── ground_truth_gold.csv      # CSV version of the same ground-truth dataset
```