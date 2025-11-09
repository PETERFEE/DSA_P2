import joblib
import numpy as np
import pandas as pd

def conf(body):
    model = joblib.load("model/naive_bayes.pkl")
    vectorizer = joblib.load("model/vectorizer.pkl")
    #message = input("Enter a test message: ")
    message = body
    X_new = vectorizer.transform([message])
    preds = model.predict(X_new)
    probs = model.predict_proba(X_new)
    label = preds[0]
    confidence = np.max(probs[0])
    #print(f"Message: {message}")
    #print(f"Predicted label: {label} (confidence: {confidence:.3f})")
    if label == "spam":
        return confidence
    else:
        return 1 - confidence