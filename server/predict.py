import joblib
import numpy as np
import pandas as pd
import os
import joblib

BASE_DIR = os.path.dirname(__file__)  # directory of this file (server/)
MODEL_DIR = os.path.join(BASE_DIR, "model")

model_path = os.path.join(MODEL_DIR, "naive_bayes.pkl")
vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

def naive_bayes(message):
    X_new = vectorizer.transform([message])
    preds = model.predict(X_new)
    probs = model.predict_proba(X_new)
    label = preds[0]                       # e.g., 0 or 1
    confidence = float(np.max(probs[0]))   #  force Python float
    if label == "spam":
        return label, confidence
    else:
        return label, (1.0 - confidence)
    #print(f"Message: {message}")
    #print(f"Predicted label: {label} (confidence: {confidence:.3f})")
    # here: call to amaan and rohan function