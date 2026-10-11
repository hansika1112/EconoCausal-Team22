# EconoCausal: Dynamic Pricing via Double Machine Learning

**Team Group:** 22
**Organization:** Infotact Solutions Internship
**Assignment ID:** ITS/DSML/1192
**Domain:** Data Science & Machine Learning

## Project Overview

This repository is the shared workspace for the EconoCausal project. The project focuses on investigating dynamic pricing using Double Machine Learning (DML). The exact business question, dataset, target variables, and evaluation requirements must be confirmed with the assigned mentor before implementation.

## Team

- Hansika Gehlot — Team Leader
- Kumbha Siva Ganesh
- Duppada Dhanalakshmi
- Hassan Baig

## Planned Workflow

1. Confirm the problem statement, dataset, deliverables, and deadline.
2. Load and inspect the approved dataset.
3. Clean the data and perform exploratory data analysis (EDA).
4. Define the causal question, treatment, outcome, and confounders with mentor guidance.
5. Build a baseline and implement an appropriate DML approach.
6. Evaluate assumptions and results using suitable metrics and diagnostics.
7. Document findings and prepare the required report and final deliverables.

## Repository Structure

```text
EconoCausal-Team22/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── evaluation/
├── reports/
│   └── figures/
├── presentation/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Recommended Python version: 3.10 or 3.11, subject to course requirements.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Collaboration Rules

- Create a separate branch for each task, such as `feature/eda` or `feature/data-cleaning`.
- Open a Pull Request for review instead of pushing directly to `main`.
- Use clear commit messages, such as `Add initial EDA notebook`.
- Never commit passwords, API keys, personal data, or private datasets.
- Document dataset sources and applicable licenses.
- Do not claim results until experiments have been completed and verified.

## Project Status

Initial repository scaffold. Dataset selection, methodology confirmation, implementation, and evaluation are pending.
