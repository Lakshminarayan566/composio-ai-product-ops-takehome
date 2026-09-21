
## AI Product Ops Research Agent

A research and analysis pipeline that evaluates **100 apps** for AI-agent integration readiness.

The project combines web search, structured LLM extraction, dataset analysis, targeted verification, and an interactive HTML case study to identify common patterns in authentication, API access, MCP availability, buildability, and integration blockers.

---

## Live Case Study

**Live website:**  
https://lakshminarayan566.github.io/composio-ai-product-ops-takehome/

**GitHub repository:**  
https://github.com/Lakshminarayan566/composio-ai-product-ops-takehome

---

## Project Overview

The objective was to research a fixed set of 100 apps and determine:

- What each app does
- Authentication methods
- Whether access is self-serve or gated
- API surface and breadth
- MCP availability
- Whether an AI-agent integration is realistically buildable
- The main integration blocker
- Evidence from official documentation

The pipeline was designed to automate the repetitive research work while keeping human verification for uncertain and high-impact claims.

---

## Key Results

### 100 apps analyzed

The research dataset contains all 100 required apps.

### Initial research outcome

- **63** apps classified as easy wins
- **14** apps identified as outreach candidates
- **23** apps requiring additional attention or having other integration constraints

> These classifications are outputs of the research pipeline and should be interpreted together with the underlying evidence and verification status.

### Verification outcome

A targeted verification sample of **20 apps** was created, with **19 supported apps** and **1 unresolved app**.

Verification status across the final 100-app dataset:

| Status | Apps |
|---|---:|
| Verified | 19 |
| Unverified | 80 |
| Unresolved | 1 |
| **Total** | **100** |

The targeted verification sample produced a **first-pass factual accuracy of 18.1% (31/171 field checks)** before document/human correction.

The 18.1% figure is a **targeted verification-sample measurement**, not an accuracy claim for all 100 apps.

---

## Main Research Dimensions

Each app was evaluated across the following dimensions:

| Dimension | Description |
|---|---|
| Category | App category such as CRM, communication, analytics, payments, etc. |
| What it does | One-line description |
| Authentication | OAuth, API keys, tokens, developer credentials, etc. |
| Access model | Self-serve or gated |
| API surface | REST, GraphQL, SDKs, webhooks, CLI, etc. |
| API breadth | Approximate integration surface and capability coverage |
| MCP | MCP support/availability |
| Buildability | Whether a useful integration can realistically be built |
| Main blocker | Primary implementation or access constraint |
| Evidence | Official documentation/source URL |
| Confidence | Confidence level from the research process |
| Verification | Whether the result was subsequently checked |

---

## Research Workflow

```text
100 required apps
       │
       ▼
App-specific web searches
       │
       ▼
Official documentation/results
       │
       ▼
Groq LLM structured extraction
       │
       ▼
Raw research dataset
       │
       ▼
Pattern analysis across all 100 apps
       │
       ▼
Targeted verification sample
       │
       ▼
Human/document verification
       │
       ▼
Final dataset + interactive case study
```

---

## How the Agent Works

The research agent uses a two-stage workflow:

### 1. Evidence discovery

For every app, the agent generates site-focused search queries intended to find official documentation, API references, authentication documentation, MCP information, and developer resources.

### 2. Structured extraction

Search results are passed to a Groq-hosted language model which extracts the required fields into a strict JSON structure.

The pipeline then saves the result into the research dataset.

### 3. Incremental persistence

Results are written after each processed app, allowing the research process to resume without losing previously completed work.

### 4. Failure handling

Search or extraction failures are recorded rather than silently discarded. Failed or incomplete apps can therefore be identified and retried separately.

---

## Human-in-the-Loop Verification

Automation is useful for broad coverage, but documentation-heavy research still requires human review.

Human verification was used to:

- Check claims against official documentation
- Resolve ambiguous authentication models
- Distinguish public APIs from gated/developer-approved access
- Confirm API and MCP availability
- Correct inaccurate or incomplete first-pass fields
- Identify unresolved cases

This separation between **automated discovery** and **document-backed verification** is intentional.

---

## Project Structure

```text
composio-ai-product-ops-takehome/
│
├── agent/
│   ├── config.py
│   └── researcher.py
│
├── analysis/
│   ├── analyze_patterns.py
│   ├── analyze_results.py
│   ├── patterns.json
│   └── patterns_report.md
│
├── data/
│   ├── apps.csv
│   └── research_results.csv
│
├── verification/
│   ├── merge_verification.py
│   ├── verification_results.csv
│   ├── verification_sample.csv
│   ├── verification_template.csv
│   └── verified_targets.csv
│
├── output/
│   ├── build_case_study.py
│   └── case-study.html
│
├── index.html
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Source Code

### Research Agent

[agent/researcher.py](agent/researcher.py)

Main research pipeline responsible for:

- App-by-app search
- Evidence collection
- LLM extraction
- Structured output
- Retry handling
- Incremental saving
- Resume support

### Configuration

[agent/config.py](agent/config.py)

Contains runtime configuration for:

- Groq API
- Model selection
- Search settings
- Request timeouts
- Retry settings

### Pattern Analysis

[analysis/analyze_patterns.py](analysis/analyze_patterns.py)

Analyzes the complete 100-app dataset to identify patterns and distributions.

### Result Analysis

[analysis/analyze_results.py](analysis/analyze_results.py)

Produces summary statistics and research-result analysis.

### Verification Merge

[verification/merge_verification.py](verification/merge_verification.py)

Merges verification outcomes into the main research dataset.

### Case Study Builder

[output/build_case_study.py](output/build_case_study.py)

Generates the final interactive HTML case study.

---

## Data Files

### Input Dataset

[data/apps.csv](data/apps.csv)

Contains the 100 required apps and the research schema.

### Research Output

[data/research_results.csv](data/research_results.csv)

Contains the automated research results for all 100 apps.

### Verification Sample

[verification/verification_sample.csv](verification/verification_sample.csv)

Contains the targeted 20-app verification sample.

### Verification Results

[verification/verification_results.csv](verification/verification_results.csv)

Contains the verification accuracy summary and verification outcomes.

### Pattern Report

[analysis/patterns_report.md](analysis/patterns_report.md)

Contains the generated pattern analysis.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Lakshminarayan566/composio-ai-product-ops-takehome.git
cd composio-ai-product-ops-takehome
```

Create and activate a virtual environment:

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

The research agent uses Groq for structured LLM extraction.

Create a local `.env` file in the project root:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-20b
GROQ_BASE_URL=https://api.groq.com/openai/v1

SEARCH_RESULTS_PER_QUERY=3
SEARCH_TIMEOUT=8
REQUEST_TIMEOUT=30
MAX_RETRIES=1
```

**Important:** `.env` is intentionally excluded from Git through `.gitignore` and is not part of the public repository.

Never commit or publish API keys.

---

## Run the Research Agent

From the project root:

```bash
python agent/researcher.py
```

The agent processes the app list and writes the results to:

```text
data/research_results.csv
```

The process is designed to save incrementally and can continue after failures.

---

## Run Pattern Analysis

```bash
python analysis/analyze_patterns.py
```

This generates:

```text
analysis/patterns.json
analysis/patterns_report.md
```

---

## Run Result Analysis

```bash
python analysis/analyze_results.py
```

---

## Run Verification Merge

```bash
python verification/merge_verification.py
```

---

## Build the Case Study

```bash
python output/build_case_study.py
```

This generates:

```text
output/case-study.html
```

The root `index.html` is the deployable version used by GitHub Pages.

---

## Case Study Features

The final HTML page includes:

- Executive summary
- 100-app research overview
- Key research findings
- Authentication/access patterns
- API surface and breadth
- MCP availability
- Buildability analysis
- Integration blockers
- Automated research workflow
- Human-in-the-loop verification
- Verification accuracy
- Limitations and known misses
- Searchable/filterable 100-app table

---

## Limitations

This project intentionally does not claim that all automated research results are perfectly verified.

The final dataset contains:

- 19 verified apps
- 80 unverified apps
- 1 unresolved app

The verification sample was targeted toward lower-confidence and failed/ambiguous cases rather than randomly sampled from the entire dataset.

Therefore:

**18.1% first-pass accuracy applies only to the targeted verification sample and should not be interpreted as the accuracy of the full 100-app dataset.**

The research pipeline is designed to surface evidence efficiently, while human/document review is still necessary for high-confidence final decisions.

---

## Reproducibility

A reviewer can reproduce the pipeline using:

```bash
pip install -r requirements.txt
```

then configure the local `.env` file and run:

```bash
python agent/researcher.py
python analysis/analyze_patterns.py
python analysis/analyze_results.py
python verification/merge_verification.py
python output/build_case_study.py
```

---

## Submission Links

### Live Case Study

https://lakshminarayan566.github.io/composio-ai-product-ops-takehome/

### Source Repository

https://github.com/Lakshminarayan566/composio-ai-product-ops-takehome

---

## Author

**Lakshminarayan**

AI/ML Engineering | Generative AI | RAG | Agentic AI | Software Engineering
