# Multi-Agent AI System
### MSc Dissertation — Danish | Glasgow Caledonian University

---

## Project Overview

A Multi-Agent AI System built with LangGraph and Groq LLaMA 3.1 that demonstrates:

- **RQ1:** Hierarchical vs Flat orchestration strategy comparison
- **RQ2:** Structured vs Unstructured prompt design comparison

Two industry domains implemented:
- Healthcare Triage (4 specialized agents)
- Supply Chain Optimisation (4 specialized agents)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| LLM | Groq LLaMA 3.1 (free) |
| Schema Validation | Pydantic v2 |
| Memory | ChromaDB |
| UI | Streamlit |
| Experiment Tracking | Weights & Biases |

---

## Setup Instructions

### 1. Clone / Extract the project

```bash
cd danish_mas_project
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API Key

Create a `.env` file in the root folder:

GROQ_API_KEY=your_groq_api_key_here

Get free API key from: https://groq.com

### 5. Run the app

```bash
streamlit run app.py
```

Open browser: http://localhost:8501

---

## Run Evaluation

To generate evaluation results (RQ1 & RQ2 comparison):

```bash
python run_evaluation.py
```

Results saved in `logs/` folder as JSON.

---

## Project Structure

danish_mas_project/
├── src/
│   ├── agents/
│   │   ├── healthcare_agents.py       ← 4 HC agents
│   │   ├── healthcare_pipeline.py     ← HC LangGraph pipeline
│   │   ├── supply_chain_agents.py     ← 4 SC agents
│   │   └── supply_chain_pipeline.py   ← SC LangGraph pipeline
│   ├── schemas/
│   │   ├── healthcare_schemas.py      ← Pydantic schemas
│   │   └── supply_chain_schemas.py    ← Pydantic schemas
│   └── evaluation/
│       └── evaluator.py               ← Evaluation framework
├── logs/                              ← Evaluation results (JSON)
├── data/                              ← Dataset folder
├── app.py                             ← Streamlit UI
├── run_evaluation.py                  ← Run full evaluation
├── requirements.txt
├── .env                               ← API keys (not shared)
└── README.md
---

## Supervisor Demo Script

### Step 1 — RQ2 Proof
- Sidebar: `hierarchical` + `unstructured` → Run → Error shown
- Sidebar: `hierarchical` + `structured` → Run → 100% success
- **Proves:** Structured prompting is essential

### Step 2 — RQ1 Proof
- Sidebar: `hierarchical` + `structured` → Run → ~6s
- Sidebar: `flat` + `structured` → Run → ~12s
- **Proves:** Hierarchical is 2x more efficient

### Step 3 — Supply Chain
- Switch domain → Run pipeline → Show results

### Step 4 — Evaluation Dashboard
- Scroll down → Open "View Evaluation Results"
- Show table + charts + key findings

---

## Key Results

| Configuration | TCR | Avg Steps | Avg Latency |
|--------------|-----|-----------|-------------|
| Hierarchical + Structured (Proposed) | 100% | 4.0 | 6.0s |
| Flat + Structured | 100% | 4.0 | 11.84s |
| Hierarchical + Unstructured | 0% | 0.0 | 4.08s |
| Flat + Unstructured | 0% | 0.0 | 4.32s |

---

## Research Findings

**RQ1:** Hierarchical orchestration is 2x faster than flat orchestration
(6.0s vs 11.84s) while maintaining the same task completion rate.

**RQ2:** Structured prompt design achieves 100% task completion rate
vs 0% with unstructured prompts — proving schema-constrained
delegation is essential for reliable multi-agent pipelines.

---

*Built with LangGraph + Groq LLaMA 3.1 | GCU MSc Big Data Technologies 2025-26*

