FROM python:3.14-slim-bookworm

# uv, copied from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# XGBoost needs the OpenMP runtime, which the slim image does not include
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Put the project's virtual environment first on the PATH
ENV PATH="/code/.venv/bin:$PATH"

# Install the locked runtime dependencies only (no notebook or dev groups)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-default-groups

# Application code and the trained model
COPY predict.py model.bin ./

EXPOSE 9696

ENTRYPOINT ["uvicorn", "predict:app", "--host", "0.0.0.0", "--port", "9696"]
