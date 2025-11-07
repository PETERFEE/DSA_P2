# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from spam_classifier import SpamDecisionTree  # Your Python spam logic

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your Chrome extension

classifier = SpamDecisionTree()

@app.route('/classify', methods=['POST'])
def classify_email():
    try:
        data = request.get_json()
        email_text = data.get('text', '')
        nb_conf = data.get('nb_conf', 0.5)
        has_name = data.get('has_name', False)

        if not email_text:
            return jsonify({'error': 'No email text provided'}), 400

        result, confidence, reasoning = classifier.classify(email_text, nb_conf, has_name)

        return jsonify({
            'classification': result,
            'confidence': confidence,
            'spam_score': reasoning.get('spam_score'),
            'reasoning_path': reasoning.get('decision_path')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("Starting spam analysis server at http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
