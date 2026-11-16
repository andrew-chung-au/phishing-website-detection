# Phishing Website Detection

A classifier and web service that predicts whether a website is phishing, from 30 coded page, URL and domain indicators. Built for the ML Zoomcamp midterm.

**Headline result:** XGBoost, test ROC AUC 0.997, precision 0.972, recall 0.966 (phishing is the positive class).

## For reviewers

This README is organised so you can score quickly, or check any criterion in depth.

- **Quick review (about 5 minutes):** read the scoring table below and follow the evidence links. Nothing needs to be run.
- **Check by running it (about 15 minutes):** follow [Reproduce and verify](#reproduce-and-verify), step by step.
- **Deep dive:** each criterion has a "Details" section further down, and [`docs/verification.md`](docs/verification.md) has the full checklist with recorded values.

### Scoring table

Criteria and point values are from [`docs/mlzoomcamp/rubric.md`](docs/mlzoomcamp/rubric.md). "Suggested" is the author's self-assessment. Please score independently.

| Criterion | Max | Suggested | Evidence (click to check) |
|---|---:|---:|---|
| Problem description | 2 | 2 | [Problem](#problem): what is predicted, who uses it, how, and what the error costs |
| EDA | 2 | 2 | [`notebook.ipynb`](notebook.ipynb) sections 1 to 6: value ranges, missing values, target balance, duplicates, mutual information, correlation, random forest and permutation importance |
| Model training | 3 | 3 | Linear and tree models, all tuned with grid search and 5-fold CV: notebook sections 7 to 9. [Details](#model-training) |
| Exporting notebook to script | 1 | 1 | [`train.py`](train.py) |
| Reproducibility | 1 | 1 | Data committed at [`data/training-dataset.arff`](data/training-dataset.arff). Notebook and script run from a clean `uv sync` ([steps](#reproduce-and-verify)) |
| Model deployment | 1 | 1 | FastAPI service in [`predict.py`](predict.py), client in [`test_predict.py`](test_predict.py) |
| Dependency and environment management | 2 | 2 | [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock), [`.python-version`](.python-version). The README gives install and environment steps ([Setup](#setup)) |
| Containerization | 2 | 2 | [`Dockerfile`](Dockerfile), with build and run commands in [Docker](#docker) |
| Cloud deployment | 2 | 2 | Deployment code: [`render.yaml`](render.yaml). Guide: [`docs/deployment.md`](docs/deployment.md). Screenshot of a working prediction: pending, see [evidence](docs/deployment.md#evidence) |
| **Total** | **16** | **16** | |

> The cloud criterion needs a screenshot or URL of a working prediction to be added to [`docs/deployment.md`](docs/deployment.md#evidence). Until then, treat the cloud row as 1.

## Problem

Phishing websites imitate legitimate ones to steal credentials and personal data. Checking each site by hand does not scale, so a model that flags likely phishing sites from measurable page, URL and domain properties can help a security team or a browser or email filter decide which sites to block or review.

This project trains a classifier that takes 30 coded indicators for a website (for example the state of its SSL certificate, the share of anchor links that point elsewhere, whether the domain uses a prefix or suffix) and predicts whether the site is phishing (1) or legitimate (0). The output is a phishing probability, which the caller can threshold. The service labels a site phishing at probability 0.5 or higher. A missed phishing site is the costlier error, so precision and recall on the phishing class are reported alongside ROC AUC.

The service takes the **coded indicator vector**, not a raw URL. Several indicators need live lookups (such as domain age and web traffic), so turning a URL into features is out of scope and is listed under [Limitations](#limitations).

## Data

UCI Machine Learning Repository, [Phishing Websites](https://archive.ics.uci.edu/dataset/327/phishing) (#327). Licence: CC BY 4.0.

- 11,055 rows, 30 features plus the `Result` target. No missing values.
- Every feature is coded -1, 0 or 1. The meaning of each value depends on the feature; see [`docs/phishing-websites-features.md`](docs/phishing-websites-features.md).
- The original `Training Dataset.arff` is committed as [`data/training-dataset.arff`](data/training-dataset.arff), so no download is needed.

## Repository structure

```
phishing-website-detection/
├── README.md
├── notebook.ipynb                 # data checks, EDA, feature importance, model selection
├── train.py                       # final training script, writes model.bin
├── model.bin                      # trained XGBoost model and feature order (pickle)
├── predict.py                     # FastAPI service
├── test_predict.py                # client that sends two example requests
├── Dockerfile
├── render.yaml                    # cloud deployment (Render)
├── .dockerignore
├── pyproject.toml                 # dependencies (uv)
├── uv.lock                        # locked versions
├── .python-version
├── data/
│   └── training-dataset.arff
├── examples/
│   ├── phishing.json              # real phishing row from the dataset
│   └── legitimate.json            # real legitimate row from the dataset
├── docs/
│   ├── deployment.md              # cloud deployment guide (Render)
│   ├── verification.md            # full verification checklist with recorded values
│   ├── plan.md                    # decisions and build plan
│   ├── phishing-websites-features.md
│   └── mlzoomcamp/                # course task, rubric, deliverables
├── LICENSE
└── .gitignore
```

## Reproduce and verify

Requires Python 3.14 or later and [uv](https://docs.astral.sh/uv/). Docker is only needed for step 5. Run all commands from the repository root. Expected output is shown so you can compare it.

### 1. Get the code and install

```bash
git clone https://github.com/andrew-chung-au/phishing-website-detection.git
cd phishing-website-detection
uv sync
```

`uv sync` creates `.venv/` and installs the locked dependencies, including the notebook tools. You do not need to activate the environment: `uv run <command>` runs inside it. To activate it anyway, run `source .venv/bin/activate`.

### 2. Train the model (about 1 to 2 minutes)

```bash
uv run python train.py
```

Expected output includes:

```
Best parameters: {'learning_rate': 0.1, 'max_depth': 8, 'n_estimators': 400}
Mean CV ROC AUC: 0.9964
```

followed by test metrics of about `auc 0.9974, precision 0.9723, recall 0.9663, f1 0.9693` and the confusion matrix `[[1204 27] [33 947]]`. The script overwrites `model.bin`. In the author's run it reproduced the committed file exactly.

### 3. Run the notebook

```bash
uv run jupyter lab
```

Open `notebook.ipynb` and choose **Kernel > Restart Kernel and Run All Cells**. It should finish without errors or warnings. Section 9 ranks XGBoost first (mean CV AUC about 0.9964), and section 10 shows test AUC about 0.997 with the same confusion matrix as above.

The notebook is also stored with its outputs, so you can read the results on GitHub without running it.

### 4. Run the service locally

Terminal 1:

```bash
uv run uvicorn predict:app --host 0.0.0.0 --port 9696
```

Terminal 2:

```bash
uv run python test_predict.py
```

Expected: `health: {'status': 'ok'}`, a phishing example with a probability near 1 (0.99994 in the author's run, `phishing: True`) and a legitimate example with a probability near 0 (0.00118, `phishing: False`).

The same with curl:

```bash
curl -s localhost:9696/health

curl -s -X POST localhost:9696/predict \
  -H 'Content-Type: application/json' \
  -d @examples/phishing.json
```

To try it in a browser, open <http://localhost:9696/> and click one of the two example buttons. For your own input, open <http://localhost:9696/docs>, expand `POST /predict`, click **Try it out** and **Execute**.

Invalid input is rejected with HTTP 422. For example, `redirect` only accepts 0 or 1:

```bash
sed 's/"redirect": 0/"redirect": -1/' examples/phishing.json \
  | curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:9696/predict \
      -H 'Content-Type: application/json' -d @-
```

Expected: a `detail` message naming the field, then `HTTP 422`. Three more invalid cases (value out of range, unknown field, missing field) are in [`docs/verification.md`](docs/verification.md), part 4.3.

Stop the service with Ctrl+C.

### 5. Run in Docker

```bash
docker build -t phishing-detection .
docker run -it --rm -p 9696:9696 phishing-detection
```

Then, from another terminal:

```bash
curl -s localhost:9696/health
uv run python test_predict.py
```

Expected: `{"status":"ok"}` and the same predictions as in step 4.

## Details by criterion

### Model training

Trained and compared in notebook sections 7 to 9:

| Model | Type | Tuned parameters |
|---|---|---|
| Majority-class baseline | baseline | none |
| Logistic regression (raw and one-hot) | linear | `C` in 0.01, 0.1, 1, 10, 100 |
| Decision tree | tree | `max_depth`, `min_samples_leaf` |
| Random forest | tree ensemble | `max_depth`, `min_samples_leaf`, `max_features` |
| XGBoost | boosted trees | `n_estimators`, `max_depth`, `learning_rate` |

Baselines are compared on the validation set. Tuning uses grid search with stratified 5-fold cross-validation on the training plus validation data, scored by ROC AUC. The grids are in the notebook's section 9 code cell, and the XGBoost grid is also in `PARAM_GRID` in [`train.py`](train.py).

### Method

1. **Data checks and EDA.** Value ranges, missing values (none), target balance (44.3% phishing), phishing rate by feature value, mutual information, correlation, and random-forest impurity and permutation importance. `sslfinal_state` and `url_of_anchor` are the strongest signals across all of these.
2. **Target.** The original `Result` column uses -1 for phishing and 1 for legitimate. It is recoded to `phishing` (1 = phishing, 0 = legitimate) so precision and recall refer to the phishing class.
3. **Split.** 60/20/20 train, validation and test, stratified on the target, seed 1. The test set is scored once, for the selected model.
4. **Selection rule.** Fixed before looking at the test set: the highest mean cross-validation ROC AUC.

### Handling duplicates

The data has 5,206 exact duplicate rows, and 64 of 5,785 unique feature configurations (1.11%) carry both labels, so a perfect score is not possible. Duplicates were **kept**, because identical feature values do not show that two rows are the same website. Because that can inflate scores (57.2% of validation rows have an identical vector in the training set), notebook section 11 repeats the comparison with duplicates removed and with identical vectors kept together.

### Results

Tuned models, 5-fold cross-validation on the training plus validation data:

| Model | Mean CV ROC AUC |
|---|---|
| XGBoost | 0.9964 |
| Random forest | 0.9961 |
| Logistic regression (one-hot) | 0.9866 |
| Decision tree | 0.9846 |

XGBoost and the random forest are effectively tied: the 0.0003 gap is smaller than the fold-to-fold standard deviation (0.0009). XGBoost was selected by the rule above.

Selected model (XGBoost) on the held-out test set (2,211 rows):

| ROC AUC | Precision | Recall | F1 | False positives | False negatives |
|---|---|---|---|---|---|
| 0.997 | 0.972 | 0.966 | 0.969 | 27 | 33 |

Precision, recall and F1 use a 0.5 threshold with phishing as the positive class.

Sensitivity to duplicates (XGBoost test ROC AUC): 0.997 with a random split, 0.990 with exact duplicates removed, and 0.995 with identical feature vectors kept in the same split. Scores drop but stay high, so the result is not explained by repeated rows alone.

### Service

[`predict.py`](predict.py) loads `model.bin` once at startup.

| Endpoint | Purpose |
|---|---|
| `POST /predict` | Takes the 30 coded values, returns `phishing_probability` and `phishing` (probability at or above 0.5) |
| `GET /health` | Returns `{"status": "ok"}` |
| `GET /` | Landing page with two example buttons (the API docs are at `/docs`) |

Pydantic rejects missing fields, values outside each feature's allowed codes, and unknown fields with HTTP 422.

### Environment and Docker

- Dependencies are in `pyproject.toml` and locked in `uv.lock`. Runtime packages are separate from the `dev` and `notebook` groups.
- The Docker image starts from `python:3.14-slim-bookworm`, installs `libgomp1` (needed by XGBoost), installs only the locked runtime dependencies (`uv sync --locked --no-default-groups`), and copies in `predict.py` and `model.bin`.

## Cloud deployment

The service deploys to [Render](https://render.com/) as a Docker web service, defined in code by [`render.yaml`](render.yaml). Render builds the repository's `Dockerfile`.

- **Guide with steps, commands and troubleshooting:** [`docs/deployment.md`](docs/deployment.md)
- **Evidence (URL and screenshot):** [`docs/deployment.md#evidence`](docs/deployment.md#evidence)

Quick version: in the Render dashboard choose **New > Blueprint**, select this repository and apply. Then run `uv run python test_predict.py https://<service-url>`.

## Limitations

- **Coded indicators, not URLs.** The service needs the 30 coded values. Producing them for a live site needs lookups that this project does not implement.
- **Old data.** The dataset was created in 2012 and donated in 2015. Phishing techniques and the web have changed since then, and this project does not check whether each indicator can still be collected today.
- **Duplicates and conflicting labels** limit what any model can learn and can make scores optimistic. Section 11 of the notebook quantifies the effect but cannot settle whether duplicate rows are the same website.
- **Tuning and evaluation overlap.** The cross-validation metrics other than the tuning score are computed on the same data used to select hyperparameters, so they are slightly optimistic. The test-set result is not affected.
- **Single public dataset.** Performance on newer sites or other data sources is not established.
- **Pickle model file.** `model.bin` needs a compatible xgboost version. `uv.lock` pins it for local runs and Docker. Only load model files you trust.

## Citation

R. Mohammad and L. McCluskey. "Phishing Websites," UCI Machine Learning Repository, 2012. [Online]. Available: https://doi.org/10.24432/C51W2X.
