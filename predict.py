"""FastAPI service that predicts whether a website is phishing.

Input: the 30 coded indicators from the UCI Phishing Websites dataset.
Output: the phishing probability and a decision at the 0.5 threshold.

Run:  uv run uvicorn predict:app --host 0.0.0.0 --port 9696
Page: http://localhost:9696/   API docs: http://localhost:9696/docs
"""

import json
import pickle
from typing import Literal

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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


# Two real rows from the dataset (same as examples/*.json), used by the landing page
EXAMPLES = {
    "phishing": {
        "having_ip_address": -1, "url_length": 1, "shortining_service": 1,
        "having_at_symbol": 1, "double_slash_redirecting": -1, "prefix_suffix": -1,
        "having_sub_domain": -1, "sslfinal_state": -1,
        "domain_registeration_length": -1, "favicon": 1, "port": 1, "https_token": -1,
        "request_url": 1, "url_of_anchor": -1, "links_in_tags": 1, "sfh": -1,
        "submitting_to_email": -1, "abnormal_url": -1, "redirect": 0,
        "on_mouseover": 1, "rightclick": 1, "popupwidnow": 1, "iframe": 1,
        "age_of_domain": -1, "dnsrecord": -1, "web_traffic": -1, "page_rank": -1,
        "google_index": 1, "links_pointing_to_page": 1, "statistical_report": -1,
    },
    "legitimate": {
        "having_ip_address": 1, "url_length": 0, "shortining_service": -1,
        "having_at_symbol": 1, "double_slash_redirecting": 1, "prefix_suffix": -1,
        "having_sub_domain": 1, "sslfinal_state": 1, "domain_registeration_length": -1,
        "favicon": 1, "port": 1, "https_token": 1, "request_url": 1,
        "url_of_anchor": 0, "links_in_tags": 0, "sfh": -1, "submitting_to_email": 1,
        "abnormal_url": 1, "redirect": 0, "on_mouseover": -1, "rightclick": 1,
        "popupwidnow": -1, "iframe": 1, "age_of_domain": -1, "dnsrecord": -1,
        "web_traffic": 0, "page_rank": -1, "google_index": 1,
        "links_pointing_to_page": 1, "statistical_report": 1,
    },
}

LANDING_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phishing Website Detection</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 640px; margin: 3rem auto; padding: 0 1rem; color: #1f2933; line-height: 1.5; }
  h1 { margin-bottom: 0.25rem; }
  .sub { color: #52606d; margin-top: 0; }
  button { font-size: 1rem; padding: 0.6rem 1rem; margin-right: 0.5rem; border: 1px solid #9aa5b1; border-radius: 6px; background: #f5f7fa; cursor: pointer; }
  button:hover { background: #e4e7eb; }
  #result { margin-top: 1.25rem; padding: 1rem; border-radius: 6px; display: none; }
  #result.phishing { background: #ffe3e3; border: 1px solid #e12d39; }
  #result.legit { background: #e3f9e5; border: 1px solid #3f9142; }
  #result.error { background: #fff3c4; border: 1px solid #cb6e17; }
  .big { font-size: 1.25rem; font-weight: 600; }
  footer { margin-top: 2rem; font-size: 0.9rem; }
</style>
</head>
<body>
<h1>Phishing Website Detection</h1>
<p class="sub">An XGBoost model that predicts whether a website is phishing from 30 coded page, URL and domain indicators.</p>
<p>Pick an example row from the dataset. The page sends its 30 indicators to <code>POST /predict</code> and shows the model's answer.</p>
<p>
  <button onclick="run('phishing')">Try a phishing site</button>
  <button onclick="run('legitimate')">Try a legitimate site</button>
</p>
<div id="result"></div>
<footer>
  <a href="/docs">API docs (try your own input)</a> &middot;
  <a href="https://github.com/andrew-chung-au/phishing-website-detection">Source code and README</a>
</footer>
<script>
const EXAMPLES = __EXAMPLES__;
async function run(name) {
  const box = document.getElementById("result");
  box.style.display = "block";
  box.className = "";
  box.textContent = "Predicting... (the first request can take a minute if the service was asleep)";
  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(EXAMPLES[name]),
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const out = await res.json();
    const pct = (out.phishing_probability * 100).toFixed(2);
    box.className = out.phishing ? "phishing" : "legit";
    box.innerHTML = '<div class="big">' + (out.phishing ? "Phishing" : "Legitimate") + "</div>"
      + "Phishing probability: " + pct + "%<br>Example sent: " + name + " row";
  } catch (err) {
    box.className = "error";
    box.textContent = "Request failed: " + err.message;
  }
}
</script>
</body>
</html>
""".replace("__EXAMPLES__", json.dumps(EXAMPLES))


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


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def index():
    # Small landing page with two example buttons; the API docs are at /docs
    return LANDING_PAGE


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(website: Website) -> PredictResponse:
    prob = predict_single(website.model_dump())
    return PredictResponse(phishing_probability=prob, phishing=prob >= THRESHOLD)
