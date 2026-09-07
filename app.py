import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import errors

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
<<<<<<< HEAD
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_NAME = "gemini-3.6-flash"
=======
MODEL_NAME = "gemini-2.5-flash"
>>>>>>> c1bba4b45a4c3b307147057105b1fbd9e59a5d63

# Safe initialization
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MAX_WORDS_PER_REQUEST = 1000 

# 🔥 ADVANCED AI DETECTOR BYPASS PROMPT (QuillBot, GPTZero Anti-Detection)
HUMANIZE_PROMPT = """You are a professional human writer and editor. Your goal is to rewrite the input text so flawlessly that it completely bypasses advanced AI detectors like QuillBot, Copyleaks, and GPTZero.

Apply these strict linguistic rules to achieve a 100% human score:
1. **Extreme Sentence Variety (Burstiness):** Do not use uniform sentence structures. Mix very short sentences (3-5 words) with medium and occasionally long, descriptive ones. This rhythm mimics real human writing.
2. **Natural Vocabulary (Low Perplexity):** Replace overused AI words and academic fluff with conversational, natural, and grounded synonyms. 
   - NEVER use words like: *furthermore, moreover, testament, delve, leverage, revolutionize, foster, parameter, utilize, dynamically, intricate, holistic, bespoke*.
   - Use standard phrases that an ordinary person would write.
3. **Imperfections & Flow:** Real humans use active voice, idioms, phrases, and write with a relaxed tone. Avoid robotic transitions like "Firstly," "In conclusion," or "It is important to note."
4. **Preserve Facts:** Keep 100% of the original meaning, context, data, and core ideas intact. Do not invent any new facts or background info.
5. **Formatting:** Return ONLY the finalized humanized text. Do not include quotes around it, do not add introductory phrases like "Here is your text," and do not provide explanations.

Text to process:
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
    if not request.is_json:
        return jsonify({"error": "Invalid request format. JSON required."}), 400

    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter or paste your text first."}), 400

    word_count = len(text.split())
    if word_count > MAX_WORDS_PER_REQUEST:
        return jsonify({
            "error": f"The free limit is {MAX_WORDS_PER_REQUEST} words. Your text contains {word_count} words."
        }), 400

    if not client:
        return jsonify({"error": "API Key is missing on the server configuration."}), 500

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=HUMANIZE_PROMPT.format(text=text),
        )
        
        output = response.text.strip()
        if not output:
            return jsonify({"error": "AI service returned an empty response. Please try again."}), 500
            
        return jsonify({"result": output})

    except errors.APIError as e:
        app.logger.error(f"Gemini API Error: {e}")
        return jsonify({"error": "AI engine is currently busy. Please try again shortly."}), 503
    except Exception as e:
        app.logger.exception("System Error")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
