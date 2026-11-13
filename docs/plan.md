# ML Midterm: Phishing Website Detection — Build Plan

**Status:** Dataset chosen on 30 October 2026.

**Assessment requirements:** Check `Projects.txt`.

## 1. Project setup

| Item | Decision |
|---|---|
| Problem | Classify websites as phishing or legitimate using 30 coded page, URL and domain indicators |
| Dataset | UCI Phishing Websites (#327): 11,055 rows, 30 features and a `Result` column |
| Source | [UCI dataset](https://archive.ics.uci.edu/dataset/327/phishing). Use the original `Training Dataset.arff`, not a Kaggle copy |
| Citation | Mohammad, R. & McCluskey, L. (2012). *Phishing Websites* [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C51W2X |
| Models | Baseline, logistic regression, decision tree, random forest and XGBoost |
| API | FastAPI + Uvicorn; `POST /predict` and `GET /health`; port 9696 |
| Environment | `uv`, with `pyproject.toml`, `uv.lock` and `.python-version` |
| Input validation | Pydantic request and response models |
| Containerization | Docker |
| Cloud bonus | Check `Projects.txt` before choosing a platform. Fly.io follows the workshop; AWS Elastic Beanstalk is an alternative if required by the assessment |
| Repository | Create a separate GitHub repo, e.g. `phishing-website-detection` |

Do not reuse code from other courses or Kaggle notebooks.

## 2. Initial dataset checks

These are preliminary findings to guide the work, not final results.

- 11,055 rows and 30 features, with values coded as -1, 0 or 1.
- `Result` contains 6,157 instances labelled 1 and 4,898 labelled -1. Check the feature documentation to confirm which label represents phishing.
- There are 5,206 duplicate rows, leaving 5,849 unique rows after exact deduplication.
- There are 64 feature combinations with conflicting labels.
- One quick, untuned five-fold cross-validation run on the deduplicated data gave:
  - Logistic regression: 91.9% accuracy
  - Decision tree (depth 6): 91.1%
  - Random forest: 94.2%

These figures are only an initial reference. Repeat the experiments as part of the proper modelling process.

**Before starting EDA:** Read `Phishing Websites Features.docx` to understand how the features are coded. I haven't read it yet.

## 3. Data preparation decisions

Settle these before modelling and explain the choices in the README.

1. **Duplicates:** Remove exact duplicate rows before splitting the data, so identical examples cannot appear in both training and validation sets.

2. **Conflicting labels:** Decide whether to keep or remove the 64 feature combinations with conflicting labels. Explain the decision and its implications.

3. **Target labels:** Check the feature documentation and recode the target so that `1` means phishing and `0` means legitimate.

4. **Data split:** Follow the course's 60/20/20 train/validation/test split, using stratification where appropriate. Keep the test set untouched until final evaluation.

5. **Metrics:** Use ROC-AUC as the main metric, alongside precision, recall and accuracy. Pay particular attention to recall for phishing websites, since missing a phishing site is an important error.

6. **API input:** Accept JSON containing the 30 coded feature values. Generating the features automatically from a raw URL is outside the scope of this project because some require external lookups.

## 4. Build phases

The estimates are approximate. The core work totals around 18.5 hours, with another 2–3 hours for cloud deployment.

| Phase | Estimated time | Tasks and deliverables |
|---|---:|---|
| 0. Setup | 0.5 h | Create repo and folder structure, initialise `uv`, set up dependencies and document how to obtain the data |
| 1. Data preparation and EDA | 5 h | Load ARFF data, rename columns, handle duplicates, check target balance and feature values, explore mutual information and correlations, and examine feature importance |
| 2. Modelling | 5 h | Train baseline, logistic regression, decision tree, random forest and XGBoost; tune using cross-validation; compare results and select a final model |
| 3. Training script | 3 h | Create `train.py` to load the data, train the selected model and save it |
| 4. API and Docker | 3 h | Build `predict.py` with FastAPI, Uvicorn and Pydantic; lock dependencies, create the Dockerfile and test the service |
| 5. Cloud bonus | 2–3 h | Deploy to the selected platform, test a prediction and capture evidence |
| 6. Documentation and final checks | 2 h | Finish README, add a simple architecture diagram and test everything from a fresh clone |

The training script can be developed alongside the API work. Adjust the estimates if the work takes longer than expected.

## 5. Environment and dependencies

Use `uv` throughout rather than Pipenv.

Initialise the project and add the dependencies needed for the application. Add development and notebook dependencies as required.

```bash
uv init
uv add pandas scikit-learn fastapi uvicorn pydantic
uv add xgboost
uv add --dev jupyter ipykernel requests
```

Add any additional packages required for loading ARFF files, plotting or analysis after confirming what the notebook needs.

Use the generated files:

- `pyproject.toml` — project configuration and dependencies.
- `uv.lock` — locked dependency versions.
- `.python-version` — Python version for the project.
- `.venv/` — local virtual environment.

Run Python commands through `uv run`, for example:

```bash
uv run python train.py
uv run uvicorn predict:app --host 0.0.0.0 --port 9696 --reload
```

On a fresh clone, use:

```bash
uv sync
```

Keep the Python version compatible with the Docker image.

## 6. Data preparation and modelling

### EDA

Use `notebook.ipynb` to:

- Load the original ARFF dataset and give the columns readable names.
- Check data types, missing values, feature values and target balance.
- Read the feature documentation and confirm the target labels.
- Identify and handle exact duplicates and conflicting labels.
- Explore feature distributions, mutual information and correlations.
- Examine feature importance where useful.

### Model training

Compare:

- A simple baseline.
- Logistic regression.
- Decision tree.
- Random forest.
- XGBoost.

Tune relevant parameters using cross-validation on the training data. Use the validation set for model selection and keep the test set untouched until the end.

Record the scores in a comparison table and explain why the final model was selected.

### Training script

Create `train.py` so that the final training process can be run outside the notebook.

It should:

1. Load the source data.
2. Apply the agreed data preparation steps.
3. Train the selected model.
4. Save the fitted model or pipeline to disk.

The model should be reproducible from the documented training process. Make sure the saved model includes any preprocessing required to make predictions on new inputs.

## 7. FastAPI prediction service

Create `predict.py` to load the saved model and expose the prediction API.

### Endpoints

- `GET /health` — return a simple health response.
- `POST /predict` — accept the 30 coded feature values and return the prediction.

Use Pydantic to define the input and output schemas. Validate that:

- All required features are present.
- Feature values use the allowed codes.
- Unexpected fields are rejected.
- The response includes a clearly defined prediction and, if supported by the chosen model, a phishing probability.

Check the feature documentation before defining the schema. Do not assume all features allow all three values.

Use scikit-learn pipelines where appropriate so preprocessing and prediction remain together in the saved model.

### Local testing

Start the service:

```bash
uv run uvicorn predict:app --host 0.0.0.0 --port 9696 --reload
```

Open the interactive API documentation at:

`http://localhost:9696/docs`

Test both endpoints, a valid prediction and invalid inputs. Also test the API using `curl` or a small Python script with `requests`.

## 8. Docker and cloud deployment

### Docker

Create a Dockerfile that:

- Uses a compatible Python base image.
- Installs `uv`.
- Copies `pyproject.toml`, `uv.lock` and `.python-version`.
- Installs the locked dependencies.
- Copies the application code and saved model.
- Starts Uvicorn on port 9696.

Build and run the container:

```bash
docker build -t phishing-website-detection .
docker run --rm -p 9696:9696 phishing-website-detection
```

Test the API from outside the container.

Check the build early, especially after adding XGBoost. Some packages may require additional system libraries.

### Cloud bonus

Confirm the assessment requirements in `Projects.txt` before choosing the platform.

The workshop uses Fly.io:

1. Install and configure the Fly CLI.
2. Deploy the Dockerised application.
3. Test a real prediction through the deployed URL.
4. Capture a screenshot or other required evidence.
5. Destroy the app when finished if it is no longer needed, and check the platform's pricing.

If the assessment specifically requires AWS Elastic Beanstalk, follow the course deployment instructions instead.

## 9. Risks and limitations

- **Data leakage:** Remove duplicates before splitting the data. Do not use the test set for model selection or tuning.
- **Conflicting labels:** Identical feature combinations can have different outcomes, limiting how accurately those cases can be classified.
- **Old dataset:** The dataset was created in 2012 and donated in 2015. Some indicators, such as `Page_Rank`, may no longer be available or meaningful in the same way.
- **Raw URL detection:** The API accepts coded features rather than arbitrary URLs. Automatic feature extraction could be a future improvement.
- **Generalisation:** Good results on this dataset do not establish how well the model will detect current phishing websites.
- **XGBoost and Docker:** Test the image build early for dependency or system-library issues.
- **Public API:** A deployed endpoint may be publicly accessible. Avoid sending sensitive information to it.
- **Model evaluation:** Report final test-set results separately from cross-validation results, and state how duplicates and conflicting labels were handled.

## 10. Final checks

- [ ] Read `Phishing Websites Features.docx` and confirm the target label meanings.
- [ ] Run the notebook from a clean state without errors.
- [ ] Run `train.py` and confirm that it saves the model or pipeline.
- [ ] Confirm that a fresh environment can be recreated with `uv sync`.
- [ ] Test `/health` and `/predict`, including invalid inputs.
- [ ] Check the interactive `/docs` page.
- [ ] Build and run Docker successfully.
- [ ] Clone the repo into a fresh directory and follow the README instructions only.
- [ ] Test the API with `curl`.
- [ ] If completing the cloud bonus, verify a prediction, capture evidence and remove the deployment when finished.
- [ ] Record the final Git commit hash.
- [ ] Work through the Quick Pre-Submission Checklist in `Projects.txt`.
