"""
AI Text Humanizer - Flask Backend
"""

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

DAILY_WORD_LIMIT = 1500

HUMANIZE_PROMPT = """You are a text humanizer. Rewrite the following text so it reads
naturally, as if written by a human — vary sentence length, remove robotic phrasing,
keep the original meaning and facts intact, do not add new information, and do not
add any preamble or explanation. Return ONLY the rewritten text, nothing else.

Text to rewrite:
{text}
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")


@app.route("/api/humanize", methods=["POST"])
def humanize():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Koi text nahi mila. Pehle text paste karein."}), 400

    word_count = len(text.split())
    if word_count > DAILY_WORD_LIMIT:
        return jsonify({
            "error": f"Free limit {DAILY_WORD_LIMIT} words hai. Aapka text {word_count} words ka hai."
        }), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "Server par GEMINI_API_KEY set nahi hai."}), 500

    payload = {
        "contents": [
            {"parts": [{"text": HUMANIZE_PROMPT.format(text=text)}]}
        ]
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        output = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return jsonify({"result": output})
    except requests.exceptions.RequestException:
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": "AI service se connect nahi ho saka. Thodi dair baad try karein."}), 502
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response from AI service."}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
