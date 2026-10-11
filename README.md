# EconoCausal: Dynamic Pricing via Double Machine Learning

Team Group No. 22 | Infotact Solutions Internship  
Assignment ID: ITS/DSML/1192  
Domain: Data Science & Machine Learning

## Project overview
This repository is the shared workspace for the EconoCausal project. The project title indicates an investigation of dynamic pricing using Double Machine Learning (DML). The exact business question, dataset, target variables, and evaluation requirements must be confirmed from the project details/training plan or with the assigned mentor before implementation.

## Team
- Hansika Gehlot — Team Leader
- Kumbha Siva Ganesh
- Duppada Dhanalakshmi
- Hassan Baig

## Planned workflow
1. Confirm the problem statement, dataset, deliverables, and deadline.
2. Load and inspect the approved dataset.
3. Clean data and perform exploratory data analysis (EDA).
4. Define the causal question, treatment, outcome, and confounders with mentor guidance.
5. Build a baseline and implement an appropriate DML approach.
6. Evaluate assumptions and results using suitable metrics/diagnostics.
7. Document findings and prepare the report, presentation, and demo.

## Repository structure
```text
EconoCausal/
├── data/
│   ├── raw/              # Keep original data out of Git if private/large
│   └── processed/        # Processed data; do not commit sensitive data
├── notebooks/
│   └── 01_eda.ipynb
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── evaluation/
├── reports/
│   ├── figures/
│   └── project_report.md
├── presentation/
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup
Recommended Python version: 3.10 or 3.11 (confirm any course-specific requirement).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Collaboration rules
- Create a separate branch for each task: `feature/eda`, `feature/data-cleaning`, etc.
- Do not push directly to `main`; open a Pull Request for review.
- Use clear commit messages, for example: `Add initial EDA notebook`.
- Never commit passwords, API keys, personal data, or private datasets.
- Add the dataset source and license/usage conditions to the documentation.
- Do not claim results until they have been produced and checked.

## Project status
Initial repository scaffold only. Dataset, methods, and findings are not yet added.
