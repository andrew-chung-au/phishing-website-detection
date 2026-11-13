"""Train the final phishing-detection model and save it to model.bin.

Mirrors notebook.ipynb:
  - sections 1-3: load the ARFF file, recode the target (1 = phishing), split 60/20/20
  - section 9:    tune XGBoost with stratified 5-fold CV, scored by ROC AUC
  - section 10:   refit on training + validation, score once on the test set

Run:  uv run python train.py
"""

import pickle

import pandas as pd
from scipy.io import arff
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from xgboost import XGBClassifier

SEED = 1
DATA_PATH = "data/training-dataset.arff"
MODEL_PATH = "model.bin"

# Same grid as the XGBoost search in the notebook (section 9).
PARAM_GRID = {
    "n_estimators": [200, 400],
    "max_depth": [3, 5, 8],
    "learning_rate": [0.05, 0.1, 0.3],
}


def load_data(path=DATA_PATH):
    raw, _ = arff.loadarff(path)
    df = pd.DataFrame(raw)

    # Decode byte strings to integers and normalise column names to lowercase
    df = df.apply(lambda s: s.str.decode("utf-8")).astype(int)
    df.columns = df.columns.str.lower()

    # The file uses -1 for phishing and 1 for legitimate.
    # Recode so that 1 = phishing and 0 = legitimate.
    df["phishing"] = (df.result == -1).astype(int)
    df = df.drop(columns="result")
    return df


def split_data(df):
    # 80% train + validation, 20% test, stratified on the target
    df_full_train, df_test = train_test_split(
        df, test_size=0.2, random_state=SEED, stratify=df.phishing
    )
    return df_full_train.reset_index(drop=True), df_test.reset_index(drop=True)


def train_model(X, y):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    # Parallelise at one level only: GridSearchCV(n_jobs=-1).
    # The model stays single-threaded (see the note in the notebook, section 9).
    search = GridSearchCV(
        XGBClassifier(random_state=SEED, eval_metric="logloss", n_jobs=1),
        PARAM_GRID,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
    )
    # GridSearchCV refits the best parameters on all rows passed in (train + validation)
    search.fit(X, y)

    print("Best parameters:", search.best_params_)
    print(f"Mean CV ROC AUC: {search.best_score_:.4f}")
    return search.best_estimator_


def evaluate(model, X, y):
    p = model.predict_proba(X)[:, 1]
    pred = (p >= 0.5).astype(int)
    return {
        "auc": roc_auc_score(y, p),
        "precision": precision_score(y, pred),
        "recall": recall_score(y, pred),
        "f1": f1_score(y, pred),
    }, confusion_matrix(y, pred)


def save_model(features, model, path=MODEL_PATH):
    # Save the feature order with the model so the service can build its input
    with open(path, "wb") as f_out:
        pickle.dump((features, model), f_out)


def main():
    df = load_data()
    features = [c for c in df.columns if c != "phishing"]
    df_full_train, df_test = split_data(df)

    model = train_model(df_full_train[features], df_full_train.phishing)

    # Sanity check against the notebook (section 10): the test ROC AUC should be about 0.997
    metrics, cm = evaluate(model, df_test[features], df_test.phishing)
    print("Test metrics:", {k: round(v, 4) for k, v in metrics.items()})
    print("Confusion matrix [[TN FP], [FN TP]]:")
    print(cm)

    save_model(features, model)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
