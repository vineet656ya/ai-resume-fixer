import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

API_URL = "https://api.perplexity.ai/chat/completions"

SYSTEM_PROMPT = (
   "You are a professional career coach and resume writing expert.\n"
    "Take the following plain-text resume and:\n"
    "- Correct grammar\n"
    "- Rewrite in ATS-optimized format\n"
    "- Add measurable impact\n"
    "- Keep it clean and minimal (no tables)\n"
    "- Tell the new ATS score and old ATS score and the mistakes in old resume at the beginning of the response, also tell how are you giving the ats score\n"
    "- Read the resume and edit accordingle and score accordingly for example score accordingly for a IT sector resume use, for freshers resume, for experienced resume etc.\n"
    "- IMPORTANT: Do not use any Markdown formatting like bolding with asterisks. The entire output must be plain text.\n"
    "- IMPORTANT: In start say 'If you see any extra Detail that is just a suggestion'\n"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fix-resume', methods=['POST'])
def fix_resume_api():
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        return jsonify({"error": "API key not found."}), 500

    data = request.json
    user_resume = data.get('resume_text', '').strip()
    if not user_resume:
        return jsonify({"error": "No resume text provided."}), 400

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_resume}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        fixed_resume_content = response_data['choices'][0]['message']['content']
        return jsonify({"fixed_resume": fixed_resume_content})
    except requests.exceptions.RequestException as e:
        error_details = f"API Request Error: {e}"
        if hasattr(e, 'response') and e.response is not None:
            error_details += f" | Status Code: {e.response.status_code} | Response: {e.response.text}"
        print(error_details)
        return jsonify({"error": "Failed to communicate with the Perplexity API."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
