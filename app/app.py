"""A tiny API, just enough code for the scanners to have something real to check."""
from flask import Flask, jsonify

app = Flask(__name__)

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
