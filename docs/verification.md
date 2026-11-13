# Verification checklist

Steps to confirm the project works. Run them in order and tick each box. Commands assume you are in the repository root.

Requirements: Python 3.14 or later, [uv](https://docs.astral.sh/uv/), and (for part 5) Docker. Part 7 repeats everything from a fresh clone.

## 1. Install

```bash
uv sync
```

- [x] Finishes without errors and creates `.venv/`

`uv sync` installs the runtime packages plus the `dev` and `notebook` groups.

## 2. Train the model

```bash
uv run python train.py
git status
```

- [x] Prints `Best parameters: {'learning_rate': 0.1, 'max_depth': 8, 'n_estimators': 400}`
- [x] Prints `Mean CV ROC AUC: 0.9964`
- [x] Test metrics are `auc 0.9974, precision 0.9723, recall 0.9663, f1 0.9693`
- [x] Confusion matrix is `[[1204 27] [33 947]]`
- [x] No `UserWarning` is printed
- [x] `model.bin` exists afterwards

These match the notebook (section 10), so the script reproduces it.

`train.py` overwrites the committed `model.bin`. Check `git status`: if `model.bin` shows as modified, the saved file differs byte for byte from the committed one. The metrics above are what matter, but note it here if it happens: not modified (author's run, 13 Nov 2026). Retraining reproduced the committed file exactly.

## 3. Run the notebook

```bash
uv run jupyter lab
```

Open `notebook.ipynb`, choose **Kernel > Restart Kernel and Run All Cells**.

- [x] Runs to the end without errors
- [x] No `UserWarning` appears in the output of the tuning cell (section 9) or the duplicate-sensitivity cell (section 11)
- [x] Section 9 ranks XGBoost first (mean CV AUC about 0.9964), then the random forest (about 0.9961)
- [x] Section 10 shows test AUC about 0.997 and `[[1204 27] [33 947]]`

## 4. Run the service locally

Terminal 1:

```bash
uv run uvicorn predict:app --host 0.0.0.0 --port 9696
```

Terminal 2 (all commands below):

### 4.1 Test client

```bash
uv run python test_predict.py
```

- [x] `health:` shows `{'status': 'ok'}`
- [x] The phishing example returns a **high** `phishing_probability` and `phishing: True`
- [x] The legitimate example returns a **low** `phishing_probability` and `phishing: False`

Recorded values (author's run, 13 Nov 2026): phishing example 0.99994, legitimate example 0.00118.

### 4.2 Same checks with curl

```bash
curl -s localhost:9696/health

curl -s -X POST localhost:9696/predict \
  -H 'Content-Type: application/json' \
  -d @examples/phishing.json

curl -s -X POST localhost:9696/predict \
  -H 'Content-Type: application/json' \
  -d @examples/legitimate.json
```

- [x] Each command returns JSON with `phishing_probability` (a number between 0 and 1) and `phishing` (true or false)

### 4.3 Input validation

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

- [x] All four print `HTTP 422` and a `detail` message naming the field

### 4.4 Root redirect

```bash
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' localhost:9696/
```

- [x] Prints `307 -> http://localhost:9696/docs`

### 4.5 Interactive docs

Open <http://localhost:9696/docs>, expand `POST /predict`, click **Try it out**, and run it.

- [x] The page loads and a request from the page returns a prediction

Stop the service with Ctrl+C.

## 5. Docker

```bash
docker build -t phishing-detection .
docker run -it --rm -p 9696:9696 phishing-detection
```

The `.` at the end of the build command is required.

In a second terminal:

```bash
curl -s localhost:9696/health
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' localhost:9696/
uv run python test_predict.py
```

Then repeat the four validation requests from part 4.3 against the container.

- [x] The build finishes without errors
- [x] The container starts and `/health` returns `{"status":"ok"}`
- [x] `/` redirects to `/docs`
- [x] `test_predict.py` gives the same predictions as in part 4.1
- [x] The four invalid requests all return HTTP 422

## 6. Deployed service

Replace `<url>` with the deployed address.

```bash
curl -s <url>/health
uv run python test_predict.py <url>
```

- [ ] `/health` responds
- [ ] The predictions match part 4.1
- [ ] A screenshot or the URL is recorded in the README

## 7. Fresh clone

In a new folder, follow **only** the README.

```bash
git clone https://github.com/andrew-chung-au/phishing-website-detection.git phishing-fresh
cd phishing-fresh
git log -1 --format=%H
```

- [ ] Parts 1, 2, 4 and 5 all pass using only the instructions in the README
- [ ] The commit hash printed above is recorded for submission: ______

## Notes

- The examples in `examples/` are two real rows from the dataset, one phishing and one legitimate.
- If `uv sync` or `docker build` fails, record the first error message here:

  ______
