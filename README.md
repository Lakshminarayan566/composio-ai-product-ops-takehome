# Composio AI Product Ops Take-home

Research agent for the 100-app API/auth/buildability assignment.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your OpenAI API key
python agent/researcher.py --start 1 --limit 5
```

Then inspect `data/research_results.csv`.

Run all 100 only after the 5-app test is successful:

```bash
python agent/researcher.py --start 1 --limit 100
```

The agent uses web search to gather evidence, sends the collected evidence to the LLM for structured extraction, writes results incrementally, and records failures instead of terminating the full run.
