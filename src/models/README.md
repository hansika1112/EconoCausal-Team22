# Model Development, Training and Evaluation

## Project
EconoCausal: Dynamic Pricing via Double Machine Learning

## Objective
Develop and evaluate a suitable Double Machine Learning (DML) approach
for the approved dynamic pricing problem.

## Prerequisites
- Confirmed and documented dataset source and license
- Dataset features and data-quality findings from the EDA task
- Confirmed causal question and proposed methodology
- Treatment variable, outcome variable, and relevant confounders
- Mentor-approved assumptions and evaluation requirements

## Planned Workflow
1. Review the selected dataset and EDA findings.
2. Define the treatment, outcome, and confounders with the team.
3. Establish a suitable baseline.
4. Select an appropriate DML estimator based on the data and methodology.
5. Split data and train nuisance models using an appropriate validation strategy.
6. Estimate the treatment effect and assess relevant assumptions.
7. Evaluate results using suitable statistical diagnostics and metrics.
8. Document results, limitations, and reproducibility details.

## Planned Modules
- Model implementation: src/models/
- Data preparation: src/data/
- Feature engineering: src/features/
- Evaluation and diagnostics: src/evaluation/

## Current Status
Planning only. Dataset, causal variables, estimator, and evaluation criteria
must be confirmed before model training.

No model results are available yet.
