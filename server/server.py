from flask import Flask, request, jsonify
from flask_cors import CORS  
from predict import naive_bayes
from spam_classifier import classify_email

app = Flask(__name__)
CORS(app)  # <-- enable CORS for all routes

@app.route('/')
def home():
    return "Spam Classifier API is running!"

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.json
        email_text = data.get('email', '')
        has_name = data.get('has_name', False)

        if not email_text:
            return jsonify({'error': 'No email text provided'}), 400

        # Step 1: Get Naive Bayes prediction + confidence
        nb_label, nb_confidence = naive_bayes(email_text)

        # Step 2: Pass the confidence to SpamDecisionTree
        classification, spam_score, reasoning , Complie_time= classify_email(email_text, nb_confidence, has_name)

        # Step 3: Return final JSON report
        response = {
            'classification': classification,
            'spam_score': spam_score,
            'nb_prediction': 'spam' if nb_label == 1 else 'ham',
            'nb_confidence': nb_confidence,
            'reasoning': reasoning,
            'Complie_time': Complie_time
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("✅ Flask server running at http://127.0.0.1:5000")
    app.run(debug=True)
