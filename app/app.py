"""A tiny API, just enough code for the scanners to have something real to check."""
import os
import secrets

from flask import Flask, jsonify
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# Signing key for CSRF tokens: from the environment in production, random per process otherwise
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
# Every POST, PUT, PATCH and DELETE must carry a valid CSRF token (fixes SonarQube python:S4502)
csrf = CSRFProtect(app)

ITEMS = [
    {"id": 1, "name": "SonarQube", "checks": "code quality and security hotspots"},
    {"id": 2, "name": "Snyk", "checks": "known vulnerabilities in dependencies"},
    {"id": 3, "name": "Amazon Inspector", "checks": "vulnerabilities in the container image"},
]


@app.get("/")
def index():
    return jsonify(service="devsecops-demo", status="ok")


@app.get("/health")
def health():
    return jsonify(status="healthy")


@app.get("/scanners")
def scanners():
    return jsonify(ITEMS)


@app.get("/scanners/<int:item_id>")
def scanner(item_id):
    for item in ITEMS:
        if item["id"] == item_id:
            return jsonify(item)
    return jsonify(error="not found"), 404
