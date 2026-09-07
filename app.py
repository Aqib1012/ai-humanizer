"""
AI Text Humanizer - Flask Backend
----------------------------------
Simple tool: user text paste karta hai, Gemini API use karke usko
"human-like" rewrite karta hai (AI patterns kam karke).

SETUP:
    pip install -r requirements.txt

    Gemini API key free mein yahan se lo:
    https://aistudio.google.com/app/apikey

    Phir terminal mein set karo (ya .env file banao):
    export GEMINI_API_KEY="your_key_here"

RUN LOCALLY:
    python app.py
    -> http://127.0.0.1:5000 pe open hoga
"""

import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key={key}"
)

# Free-tier daily word limit per visitor (session-based, simple version).
# Production mein isko IP/DB based rate limiting se replace karna behtar hoga.
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
            GEMINI_URL.format(key=GEMINI_API_KEY),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        output = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return jsonify({"result": output})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API error: {str(e)}"}), 502
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response from AI service."}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
