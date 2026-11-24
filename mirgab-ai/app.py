"""Mirgab AI web app + REST API.

    python app.py            ->  http://localhost:5000
    POST /api/analyze        {"text": "...", "url": "..."}
    POST /api/report         {"url": "...", "category": "...", "note": "..."}
    GET  /api/stats          aggregated, anonymised dashboard data
"""
import os

from flask import Flask, jsonify, render_template, request

from mirgab import analyze, storage
from mirgab.url_analyzer import analyze_url

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
MAX_LEN = 5000


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "")[:MAX_LEN]
    url = (data.get("url") or "")[:2000]
    if not text.strip() and not url.strip():
        return jsonify({"error": "empty input"}), 400
    return jsonify(analyze(text=text, url=url))


@app.post("/api/report")
def api_report():
    data = request.get_json(silent=True) or request.form
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400
    r = analyze_url(url)
    domain = r["registered_domain"] or r["host"]
    if r["official"]:
        return jsonify({"ok": False, "message": "official domain - cannot be reported"}), 400
    storage.add_report(domain, data.get("category", ""), data.get("note", ""))
    return jsonify({"ok": True, "domain": domain, "reports": storage.report_count(domain)})


@app.get("/api/stats")
def api_stats():
    return jsonify(storage.stats())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
