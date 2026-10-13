# Double Machine Learning (DML) Research and Methodology

## Project
EconoCausal: Dynamic Pricing via Double Machine Learning

## 1. Research Objective
Investigate how Double Machine Learning can estimate the causal effect
of pricing decisions on a suitable business outcome.

## 2. Core DML Concept
DML uses machine learning to estimate:
- The outcome model: outcome as a function of treatment and controls.
- The treatment model: treatment as a function of observed controls.

A final estimation stage uses these predictions to estimate the treatment
effect while reducing sensitivity to nuisance-model estimation.

## 3. Variables to Confirm
- Treatment (T): the price or pricing intervention, subject to dataset availability.
- Outcome (Y): a suitable business outcome, such as units sold or revenue,
  subject to dataset availability.
- Confounders (W): observed factors that influence both pricing decisions
  and the outcome.
- Effect modifiers (X): observed features used to examine how effects differ.

These are candidate concepts, not confirmed dataset columns.

## 4. Proposed Workflow
1. Review the selected dataset, source, license, and data quality.
2. Define the causal question and variables with the team and mentor.
3. Assess whether relevant confounders are observed and treatment variation exists.
4. Establish a baseline model.
5. Select a suitable DML estimator and nuisance learners.
6. Use an appropriate validation and cross-fitting strategy.
7. Estimate treatment effects and uncertainty.
8. Document diagnostics, assumptions, limitations, and results.

## 5. Assumptions and Risks
- Relevant confounders are observed and appropriately controlled.
- Treatment has sufficient variation and overlap across relevant observations.
- The causal question and timing of variables are correctly specified.
- Post-treatment variables and inappropriate controls are avoided.
- Results are interpreted as causal only if identification assumptions are defensible.

## 6. Evaluation Plan
After the dataset and method are confirmed:
- Evaluate nuisance-model performance using suitable metrics.
- Report treatment-effect estimates and confidence intervals where supported.
- Check overlap, sensitivity, and robustness where feasible.
- Compare with an appropriate baseline and document limitations.

## 7. Pending Decisions
- Approved dataset and license
- Exact causal question
- Treatment, outcome, controls, and effect modifiers
- Appropriate estimator and nuisance learners
- Mentor-approved evaluation requirements

## Status
Initial research draft only. No dataset-specific model has been trained,
and no empirical results are claimed.
