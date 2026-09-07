"""
AI Text Humanizer - Flask Backend
"""

import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_NAME = "gemini-2.5-flash"

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

    if not client:
        return jsonify({"error": "Server par GEMINI_API_KEY set nahi hai."}), 500

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=HUMANIZE_PROMPT.format(text=text),
        )
        output = response.text.strip()
        return jsonify({"result": output})
    except Exception:
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": "AI service se connect nahi ho saka. Thodi dair baad try karein."}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
