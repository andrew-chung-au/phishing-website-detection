# Phishing Website Detection

## Problem

Phishing websites imitate legitimate ones to steal credentials and personal data. Checking each site by hand does not scale, so a model that flags likely phishing sites from measurable page, URL and domain properties can help a security team or a browser or email filter decide which sites to block or review.

This project trains a classifier that takes 30 coded indicators for a website (for example the state of its SSL certificate, the share of anchor links that point elsewhere, whether the URL uses a prefix or suffix in the domain) and predicts whether the site is phishing (1) or legitimate (0). The output is a phishing probability, which the caller can threshold. A missed phishing site is the costlier error, so precision and recall on the phishing class are reported alongside ROC AUC.

The service takes the **coded indicator vector**, not a raw URL. Several indicators need live lookups (such as domain age and web traffic), so turning a URL into features is out of scope here and is listed as a next step.

## Data

UCI Machine Learning Repository, [Phishing Websites](https://archive.ics.uci.edu/dataset/327/phishing) (#327).

- 11,055 rows, 30 features plus the `Result` target, no missing values.
- Every feature is coded -1, 0 or 1. The meaning of each value depends on the feature; see [`docs/phishing-websites-features.md`](docs/phishing-websites-features.md).
- The original `Training Dataset.arff` from the UCI zip is committed as `data/training-dataset.arff`, so no download is needed.
- Licence: CC BY 4.0.

## Repository structure

```
phishing-website-detection/
├── README.md
├── notebook.ipynb                 # data checks, EDA, feature importance, model selection
├── pyproject.toml                 # dependencies (uv)
├── uv.lock                        # locked versions
├── data/
│   └── training-dataset.arff
├── docs/
│   ├── phishing-websites-features.md
│   ├── plan.md
│   └── mlzoomcamp/                # course task and rubric
├── LICENSE
└── .gitignore
```

Still to add: `train.py`, `predict.py`, a test client, `model.bin`, `Dockerfile`, `.dockerignore`, `.python-version`, and the cloud deployment files.

## Setup

Requires Python 3.14 or later and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/andrew-chung-au/phishing-website-detection.git
cd phishing-website-detection
uv sync                # creates .venv and installs the locked dependencies
uv run jupyter lab     # then open notebook.ipynb
```

`uv run <command>` runs a command inside the project environment, so there is no need to activate it manually.

## Approach

The full analysis is in [`notebook.ipynb`](notebook.ipynb).

1. **Data checks and EDA.** Value ranges, missing values (none), target balance (44.3% phishing), phishing rate by feature value, mutual information, correlation, and random-forest impurity and permutation importance. `sslfinal_state` and `url_of_anchor` are the strongest signals across all of these.
2. **Target.** The original `Result` column uses -1 for phishing and 1 for legitimate. It is recoded to `phishing` (1 = phishing, 0 = legitimate) so precision and recall refer to the phishing class.
3. **Split.** 60/20/20 train, validation and test, stratified on the target. The test set is used once, for the selected model.
4. **Models.** Majority-class baseline, logistic regression (raw and one-hot), decision tree, random forest and XGBoost. Each is tuned with stratified 5-fold cross-validation, scored by ROC AUC.
5. **Selection rule.** Fixed before looking at the test set: the highest mean cross-validation ROC AUC.

### Handling duplicates

The data has 5,206 exact duplicate rows, and 64 of 5,785 unique feature configurations (1.11%) carry both labels, so a perfect score is not possible. Duplicates were **kept**, because identical feature values do not show that two rows are the same website. Because that can inflate scores (57.2% of validation rows have an identical vector in the training set), the notebook repeats the comparison with duplicates removed and with identical vectors kept together (section 11).

## Results

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

These are results on this dataset only.

## Limitations

- **Coded indicators, not URLs.** The service needs the 30 coded values. Producing them for a live site needs lookups that this project does not implement.
- **Old data.** The dataset was created in 2012 and donated in 2015. Phishing techniques and the web have changed since then, and this project does not check whether each indicator can still be collected today. Results describe this snapshot only.
- **Duplicates and conflicting labels** limit what any model can learn and can make scores optimistic. Section 11 of the notebook quantifies the effect but cannot settle whether duplicate rows are the same website.
- **Tuning and evaluation overlap.** The cross-validation metrics other than the tuning score are computed on the same data used to select hyperparameters, so they are slightly optimistic. The test-set result is not affected by this.
- **Single public dataset.** Performance on newer sites or other data sources is not established.

## Citation

R. Mohammad and L. McCluskey. "Phishing Websites," UCI Machine Learning Repository, 2012. [Online]. Available: https://doi.org/10.24432/C51W2X.
