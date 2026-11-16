# Cloud deployment guide (Render)

The service is deployed to [Render](https://render.com/docs/blueprint-spec) as a Docker web service. Render builds the repository's own [`Dockerfile`](../Dockerfile), so the deployed container is the one tested locally. The deployment is defined in code by [`render.yaml`](../render.yaml) in the repository root:

```yaml
services:
  - type: web
    name: phishing-detection
    runtime: docker
    plan: free
    healthCheckPath: /health
    envVars:
      # The Dockerfile serves on 9696; tell Render which port to route to
      - key: PORT
        value: "9696"
```

| Setting | Purpose |
|---|---|
| `runtime: docker` | Build and run the repository's `Dockerfile` |
| `plan: free` | Use Render's free instance type |
| `healthCheckPath: /health` | Render checks this endpoint (returns `{"status": "ok"}`) before routing traffic |
| `PORT=9696` | The Dockerfile starts Uvicorn on 9696, so Render must route to that port |

## Deploy

Prerequisites: a [Render](https://dashboard.render.com) account connected to GitHub, and this repository (or your fork) on GitHub with `render.yaml` in the root of the branch you deploy.

1. In the Render dashboard, choose **New > Blueprint**.
2. Select the repository, and the branch that contains `render.yaml`.
3. Render reads the file and lists the `phishing-detection` service. Click **Apply**.
4. Wait for the Docker build to finish (a few minutes; the logs show progress). The service shows **Live** when it is ready.
5. Copy the service URL from the top of the service page. It looks like `https://phishing-detection-xxxx.onrender.com`.

## Test

```bash
curl -s https://<service-url>/health
uv run python test_predict.py https://<service-url>
```

Expected: `{"status":"ok"}`, a phishing probability near 1 for the phishing example (0.99994 locally) and near 0 for the legitimate example (0.00118 locally). You can also open `https://<service-url>/docs` and run `POST /predict` from the page.

On the free plan the service sleeps when idle, so the first request can take about a minute.

## Troubleshooting

- **Build fails:** read the first error in the build log.
- **"No open ports detected" or no response:** check that the `PORT` environment variable is `9696` under **Environment**.

## Remove the deployment

Open the service in the Render dashboard, then **Settings > Delete Service**. A deployed endpoint is public, so do not send sensitive data to it.
