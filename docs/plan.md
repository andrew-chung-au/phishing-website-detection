# ML Midterm: Phishing Website Detection — Build Plan

**Status (13 November 2026):** Phases 0 to 4 are done. Phase 5 (cloud bonus) and phase 6 (final documentation and checks) remain.

**Assessment requirements:** `docs/mlzoomcamp/task.md` and `docs/mlzoomcamp/rubric.md`. Cloud deployment is a bonus in the task description and 2 of the rubric's 16 points.

## 1. Project setup

| Item | Decision |
|---|---|
| Problem | Classify websites as phishing or legitimate using 30 coded page, URL and domain indicators |
| Dataset | UCI Phishing Websites (#327): 11,055 rows, 30 features and a `Result` column |
| Source | [UCI dataset](https://archive.ics.uci.edu/dataset/327/phishing). The original `Training Dataset.arff` is committed as `data/training-dataset.arff` |
| Citation | Mohammad, R. & McCluskey, L. (2012). *Phishing Websites* [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C51W2X |
| Models | Majority-class baseline, logistic regression (raw and one-hot), decision tree, random forest and XGBoost |
| API | FastAPI + Uvicorn; `POST /predict`, `GET /health`, `GET /` (redirects to `/docs`); port 9696 |
| Environment | `uv`, with `pyproject.toml`, `uv.lock` and `.python-version` |
| Input validation | Pydantic request and response models |
| Containerization | Docker (`python:3.14-slim-bookworm`) |
| Cloud bonus | Not yet chosen. Fly.io follows the workshop; AWS Elastic Beanstalk is the module's other option |
| Repository | `phishing-website-detection`. No code from other courses or Kaggle notebooks |

## 2. Dataset checks (confirmed in the notebook)

- 11,055 rows and 30 features, all coded -1, 0 or 1. No missing values.
- The original `Result` uses -1 for phishing and 1 for legitimate. It is recoded to `phishing` (1 = phishing, 0 = legitimate). 44.3% of rows are phishing.
- 5,206 exact duplicate rows. 5,785 unique feature configurations, of which 64 (1.11%) have conflicting labels.
- Some features take only two values and some three; `redirect` takes only 0 or 1. The API schema follows the ARFF header, not an assumption that every feature allows all three.

## 3. Data preparation decisions (made)

1. **Duplicates: kept.** Identical feature values do not show that two rows are the same website, so removing them could discard valid observations and change the class balance. Because keeping them can inflate scores (57.2% of validation rows have an identical vector in the training set), notebook section 11 repeats the comparison with duplicates removed and with identical vectors grouped together. XGBoost's test ROC AUC is 0.997 with a random split, 0.990 with duplicates removed and 0.995 grouped.
2. **Conflicting labels: kept.** They are documented as a limitation: they cap what any model can learn from these features.
3. **Target:** `phishing` = 1 for the original label -1.
4. **Split:** 60/20/20 train, validation and test, stratified on the target, seed 1. The validation set compares baselines at default settings. Tuning and model selection use stratified 5-fold cross-validation on the training plus validation data, scored by ROC AUC. The test set is scored once, for the selected model.
5. **Metrics:** ROC AUC as the headline metric, plus precision, recall and F1 at a 0.5 threshold, with phishing as the positive class. Missing a phishing site is the costlier error.
6. **API input:** JSON with the 30 coded feature values. Generating features from a raw URL is out of scope because some need live lookups.

## 4. Build phases

| Phase | Estimated time | Status | Deliverable |
|---|---:|---|---|
| 0. Setup | 0.5 h | Done | Repo, `uv`, data committed |
| 1. Data preparation and EDA | 5 h | Done | `notebook.ipynb` sections 1 to 6 |
| 2. Modelling | 5 h | Done | `notebook.ipynb` sections 7 to 12 |
| 3. Training script | 3 h | Done | `train.py` reproduces the notebook's final model and saves `model.bin` |
| 4. API and Docker | 3 h | Done | `predict.py`, `test_predict.py`, `Dockerfile`, `.dockerignore`, `examples/` |
| 5. Cloud bonus | 2–3 h | To do | Deployment, a tested prediction and evidence |
| 6. Documentation and final checks | 2 h | In progress | README, architecture diagram, `docs/verification.md`, fresh-clone test |

## 5. Environment and dependencies

`uv` throughout. Dependencies are split into groups:

- **Runtime** (`[project] dependencies`): fastapi, uvicorn, pandas, scikit-learn, scipy, xgboost.
- **`dev`**: ipykernel, requests.
- **`notebook`**: jupyter, matplotlib, seaborn.

`[tool.uv] default-groups = ["dev", "notebook"]` makes a plain `uv sync` install everything for local work, while the Docker build skips both groups (`--no-default-groups`) to keep Jupyter out of the image.

Files: `pyproject.toml`, `uv.lock`, `.python-version`. The project requires Python 3.14 or later, and the Docker base image uses 3.14.

```bash
uv sync
uv run python train.py
uv run uvicorn predict:app --host 0.0.0.0 --port 9696
```

## 6. Modelling

`notebook.ipynb`:

- Sections 1 to 6: loading, target recoding, data-quality checks, split, EDA (phishing rate by feature value, mutual information, correlation, random-forest impurity and permutation importance).
- Sections 7 to 10: baselines on the validation set, tuned models by 5-fold CV, and the one-time test-set evaluation.
- Section 11: duplicate-sensitivity check. Section 12: conclusions and limitations.

Tuned CV ROC AUC: XGBoost 0.9964, random forest 0.9961, logistic regression 0.9866, decision tree 0.9846. XGBoost and the forest are effectively tied (the gap is smaller than the 0.0009 fold-to-fold standard deviation). XGBoost was selected by a rule fixed before looking at the test set. On the test set: AUC 0.997, precision 0.972, recall 0.966, F1 0.969, with 27 false positives and 33 false negatives.

Parallelism: only `GridSearchCV` uses `n_jobs=-1`. The models stay single-threaded, which avoids scikit-learn's false-alarm `delayed`/`Parallel` warning caused by nested parallelism (scikit-learn issue #35089).

### Training script

`train.py` loads the ARFF file, recodes the target, makes the same split, reruns the XGBoost grid search, refits on training plus validation, checks the test metrics, and saves `(features, model)` to `model.bin`. The final winning parameters are `learning_rate=0.1, max_depth=8, n_estimators=400`. There is no preprocessing step, so the saved file is the fitted XGBoost model plus the feature order, not a scikit-learn pipeline.

## 7. FastAPI prediction service

`predict.py` loads `model.bin` once at startup.

- `GET /health` returns `{"status": "ok"}`.
- `POST /predict` accepts the 30 coded values and returns `phishing_probability` and `phishing` (probability at or above 0.5).
- `GET /` redirects to `/docs`.

Pydantic rejects missing fields, values outside each feature's allowed codes, and unknown fields (HTTP 422). Local test steps are in `docs/verification.md`.

## 8. Docker and cloud deployment

### Docker

The Dockerfile:

- Starts from `python:3.14-slim-bookworm` and copies in `uv`.
- Installs `libgomp1`, which XGBoost needs and the slim image lacks.
- Copies `pyproject.toml` and `uv.lock`, then runs `uv sync --locked --no-default-groups`.
- Copies `predict.py` and `model.bin`, and starts Uvicorn on port 9696.

```bash
docker build -t phishing-detection .
docker run -it --rm -p 9696:9696 phishing-detection
```

### Cloud bonus (to do)

The task counts cloud deployment as a bonus. The rubric awards 2 points for deployment code plus a URL, screenshot or video of a working prediction.

The workshop uses Fly.io:

1. Install and configure the Fly CLI.
2. Deploy the Dockerised application.
3. Test a real prediction with `uv run python test_predict.py <url>`.
4. Capture a screenshot and record the URL.
5. Destroy the app when finished, and check the platform's pricing first.

## 9. Risks and limitations

- **Data leakage:** duplicates were kept, so some validation and test rows share a feature vector with training rows. Section 11 of the notebook measures the effect.
- **Conflicting labels:** identical feature combinations can have different outcomes, which limits accuracy on those cases.
- **Old dataset:** created in 2012 and donated in 2015. The project does not check whether each indicator can still be collected today.
- **Raw URL detection:** the API accepts coded features, not URLs.
- **Generalisation:** results are on one public dataset and do not establish performance on current phishing sites.
- **Model file and library versions:** `model.bin` is a pickle, so loading it needs a compatible xgboost version. The locked dependencies in `uv.lock` pin this for local runs and for Docker.
- **Public API:** a deployed endpoint may be publicly accessible. Do not send sensitive information to it.
- **Evaluation:** cross-validation metrics other than the tuning score are computed on the data used to select hyperparameters. The test set is not affected.

XGBoost in a slim Docker image was a listed risk. It is resolved: the build needs `libgomp1`.

## 10. Checks

Commands for each check are in `docs/verification.md`.

**Data and notebook**
- [x] Confirm which `Result` value means phishing and that it matches the notebook (-1 = phishing, 1 = legitimate). Checked against the UCI dataset description (6,157 legitimate and 4,898 phishing rows, matching the data) and the data itself (`sslfinal_state = 1` is 11% phishing, `-1` is 86%).
- [x] Restart the notebook and run all cells; it finishes with no errors or warnings.

**Training and environment**
- [x] Delete `.venv`, run `uv sync`, and confirm it installs everything from scratch.
- [x] Run `train.py` and confirm the numbers match the notebook.

**Service**
- [x] Start the service and send the two examples; predictions are sensible.
- [x] Send the four invalid requests; each is rejected with a clear message.
- [x] Open `/docs` and run a prediction from the page.

**Docker**
- [x] Build the image and run the container; predictions match the local service.

**Repository and documentation**
- [ ] Commit and push everything; `git status` is clean.
- [ ] Complete the README: problem, install, train, run the service, Docker.
- [ ] Clone the repo into a new folder and get it working using only the README.

**Cloud (bonus)**
- [ ] Deploy, test a prediction, add the URL or a screenshot to the README, then remove the deployment.

- [ ] Record the commit hash.
