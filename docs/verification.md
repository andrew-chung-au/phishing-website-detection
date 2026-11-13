# Verification checklist

Steps to confirm the project works from a fresh clone. Run them in order and tick each box. Commands assume you are in the repository root.

Requirements: Python 3.14 or later, [uv](https://docs.astral.sh/uv/), and (for part 4) Docker.

## 1. Install

```bash
uv sync
```

- [ ] Finishes without errors and creates `.venv/`

## 2. Train the model

```bash
uv run python train.py
```

- [ ] Prints `Best parameters: {'learning_rate': 0.1, 'max_depth': 8, 'n_estimators': 400}`
- [ ] Prints `Mean CV ROC AUC: 0.9964`
- [ ] Test metrics are `auc 0.9974, precision 0.9723, recall 0.9663, f1 0.9693`
- [ ] Confusion matrix is `[[1204 27] [33 947]]`
- [ ] No `UserWarning` is printed
- [ ] `model.bin` exists afterwards

These match the notebook (section 10), which shows the script reproduces it.

## 3. Run the service locally

Terminal 1:

```bash
uv run uvicorn predict:app --host 0.0.0.0 --port 9696
```

Terminal 2 (all commands below):

### 3.1 Test client

```bash
uv run python test_predict.py
```

- [ ] `health:` shows `{'status': 'ok'}`
- [ ] The phishing example returns a **high** `phishing_probability` and `phishing: True`
- [ ] The legitimate example returns a **low** `phishing_probability` and `phishing: False`

Result when run: phishing example ______ , legitimate example ______

### 3.2 Same checks with curl

```bash
curl -s localhost:9696/health

curl -s -X POST localhost:9696/predict \
  -H 'Content-Type: application/json' \
  -d @examples/phishing.json

curl -s -X POST localhost:9696/predict \
  -H 'Content-Type: application/json' \
  -d @examples/legitimate.json
```

- [ ] Each command returns JSON with `phishing_probability` (a number between 0 and 1) and `phishing` (true or false)

### 3.3 Input validation

Each request below should be **rejected** with HTTP 422. The `-w` flag prints the status code.

```bash
# A value that is not allowed for this feature (redirect only accepts 0 or 1)
sed 's/"redirect": 0/"redirect": -1/' examples/phishing.json \
  | curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:9696/predict \
      -H 'Content-Type: application/json' -d @-

# A value outside -1, 0, 1
sed 's/"sslfinal_state": -1/"sslfinal_state": 5/' examples/phishing.json \
  | curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:9696/predict \
      -H 'Content-Type: application/json' -d @-

# An unknown extra field
sed 's/"redirect": 0,/"redirect": 0, "whatever": 1,/' examples/phishing.json \
  | curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:9696/predict \
      -H 'Content-Type: application/json' -d @-

# A missing field (drops the iframe line)
grep -v '"iframe"' examples/phishing.json \
  | curl -s -w '\nHTTP %{http_code}\n' -X POST localhost:9696/predict \
      -H 'Content-Type: application/json' -d @-
```

- [ ] All four print `HTTP 422` and a `detail` message naming the field

### 3.4 Interactive docs

Open <http://localhost:9696/docs>, expand `POST /predict`, click **Try it out**, and run it.

- [ ] The page loads and a request from the page returns a prediction

Stop the service with Ctrl+C.

## 4. Docker

```bash
docker build -t phishing-detection .
docker run -it --rm -p 9696:9696 phishing-detection
```

In a second terminal:

```bash
curl -s localhost:9696/health
uv run python test_predict.py
```

- [ ] The build finishes without errors
- [ ] The container starts and `/health` returns `{"status":"ok"}`
- [ ] `test_predict.py` gives the same predictions as in part 3.1

## 5. Deployed service

Replace `<url>` with the deployed address.

```bash
curl -s <url>/health
uv run python test_predict.py <url>
```

- [ ] `/health` responds
- [ ] The predictions match part 3.1

## Notes

- The examples in `examples/` are two real rows from the dataset, one phishing and one legitimate.
- If `uv sync` or `docker build` fails, record the first error message here:

  ______
