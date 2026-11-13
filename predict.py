"""FastAPI service that predicts whether a website is phishing.

Input: the 30 coded indicators from the UCI Phishing Websites dataset.
Output: the phishing probability and a decision at the 0.5 threshold.

Run:  uv run uvicorn predict:app --host 0.0.0.0 --port 9696
Docs: http://localhost:9696/docs
"""

import pickle
from typing import Literal

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict

MODEL_PATH = "model.bin"
THRESHOLD = 0.5

# Allowed values per feature, taken from the dataset's ARFF header
Binary = Literal[-1, 1]
Ternary = Literal[-1, 0, 1]
ZeroOne = Literal[0, 1]


class Website(BaseModel):
    """The 30 coded indicators. Field order matches the training data."""

    model_config = ConfigDict(extra="forbid")

    having_ip_address: Binary
    url_length: Ternary
    shortining_service: Binary
    having_at_symbol: Binary
    double_slash_redirecting: Binary
    prefix_suffix: Binary
    having_sub_domain: Ternary
    sslfinal_state: Ternary
    domain_registeration_length: Binary
    favicon: Binary
    port: Binary
    https_token: Binary
    request_url: Binary
    url_of_anchor: Ternary
    links_in_tags: Ternary
    sfh: Ternary
    submitting_to_email: Binary
    abnormal_url: Binary
    redirect: ZeroOne
    on_mouseover: Binary
    rightclick: Binary
    popupwidnow: Binary
    iframe: Binary
    age_of_domain: Binary
    dnsrecord: Binary
    web_traffic: Ternary
    page_rank: Binary
    google_index: Binary
    links_pointing_to_page: Ternary
    statistical_report: Binary


class PredictResponse(BaseModel):
    phishing_probability: float
    phishing: bool


app = FastAPI(title="phishing-website-detection")

# Load the model once, when the service starts
with open(MODEL_PATH, "rb") as f_in:
    features, model = pickle.load(f_in)


def predict_single(website: dict) -> float:
    # Build the row in the same column order used for training
    X = pd.DataFrame([website], columns=features)
    return float(model.predict_proba(X)[0, 1])


@app.get("/", include_in_schema=False)
def index():
    # Send visitors to the interactive API docs
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(website: Website) -> PredictResponse:
    prob = predict_single(website.model_dump())
    return PredictResponse(phishing_probability=prob, phishing=prob >= THRESHOLD)
