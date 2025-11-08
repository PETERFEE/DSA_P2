from flask import Flask, request, make_response,jsonify
from flask_cors import CORS  
from predict import naive_bayes
from decision_tree import classify_email
from three_pass_rule import ruleFilter
import traceback

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

        if not email_text:
            return jsonify({'error': 'No email text provided'}), 400

        nb_label, nb_confidence = naive_bayes(email_text)
        classification, spam_score, reasoning, compile_time = classify_email(email_text, nb_confidence)
        classification2, spam_score2, compile_time2 = ruleFilter(email_text, nb_confidence)

        response = {
            'decision_tree': {
                'classification': classification,
                'spam_score': spam_score,
                'reasoning': reasoning,
                'compile_time': compile_time
            },
            'rule_filter': {
                'classification': classification2,
                'spam_score': spam_score2,
                'compile_time': compile_time2
            },
            'nb_prediction': 'spam' if nb_label == 1 else 'ham',
            'nb_confidence': nb_confidence
        }

        resp = make_response(jsonify(response))
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
        return resp

    except Exception as e:
        print("⚠️ ERROR during /classify:", e)
        traceback.print_exc()  # <-- this shows the full traceback
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("✅ Flask server running at http://127.0.0.1:5000")
    app.run(debug=True)
