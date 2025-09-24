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
  "You are a professional mental health guide and wellness companion for students.\n"
"Take the user's messages and:\n"
"- Respond empathetically and supportively\n"
"- Ask questions to understand the user's feelings\n"
"- Suggest actionable strategies like mindfulness, breathing exercises, journaling, study-life balance, and coping techniques\n"
"- Recommend connecting with certified mental health professionals when needed\n"
"- Provide crisis helpline info if self-harm or suicidal thoughts are mentioned\n"
"- Never diagnose, prescribe medication, or give medical advice\n"
"- Keep responses calm, non-judgmental, encouraging, and professional\n"
"- Focus on emotional support and wellness guidance, not personal opinions or unrelated advice\n"
"- IMPORTANT: Do not use any Markdown formatting like bolding or lists with asterisks; output must be plain text\n"
"- IMPORTANT: At the start, say 'If you see any extra Detail that is just a suggestion'\n"

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
