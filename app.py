from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# function imported for alg 1
try:
    from spam_classifier import classify_spam
except ImportError:
    print("Error: Could not find 'spam_classifier.py' or 'classify_spam' function.")

    def classify_spam(email_text, nb_confidence, has_recipient_name):
        return "error", 0.0, {"error": "Classifier not found"}

app = Flask(__name__)

CORS(app)

@app.route('/generate', methods=['POST'])
def generate_analysis():
    try:
        data = request.get_json()

        email_text = data.get('text')
        nb_conf = data.get('nb_confidence', 0.5)
        has_name = data.get('has_name', False)

        if not email_text:
            return jsonify({"error": "No 'text' field provided"}), 400

        classification, confidence, reasoning_dict = classify_spam(
            email_text,
            nb_conf,
            has_name
        )

        return jsonify({
            "classification": classification,
            "confidence": confidence,
            "spam_score": reasoning_dict.get('spam_score'),
            "reasoning_path": reasoning_dict.get('decision_path')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("Starting spam analysis server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)