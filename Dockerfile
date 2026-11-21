FROM python:3.13-slim

# Run as a normal user, not root
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY app/requirements.txt .
# Wheels only (no setup scripts run) and every package checked against its locked hash
RUN pip install --no-cache-dir --only-binary :all: --require-hashes -r requirements.txt

COPY app/app.py .
USER appuser

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
