# Spam or Ham - Gmail Spam Detection Chrome Extension
A Chrome extension that helps detect spam emails using machine learning. This extension uses a combination of Naive Bayes classification and a decision tree algorithm to provide accurate spam detection for Gmail messages.



   - Required Python packages:
     ```
     flask
     flask-cors
     scikit-learn
     joblib
     pandas
     numpy
     ```

## Installation

### 1. Python Backend Setup


1. Install required Python packages:
   ```bash
   python -m pip install flask flask-cors scikit-learn joblib pandas numpy
   ```

3. Navigate to the server directory:
   and Start the Flask server:
   
   python server.py
   
   The server will run at http://127.0.0.1:5000

### 2. Chrome Extension Setup

1. Open Google Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked"
5. Navigate to the `Chorme_extension` folder in this project and select it
6. The extension icon should appear in your Chrome toolbar

## Usage

1. Make sure the Python backend server is running
2. Open Gmail in Chrome
3. Click the extension icon in the toolbar
4. Click "Scan Email" or paste text 
6. The extension will show whether the email is likely spam or ham 

## Features

- Machine learning-based spam detection
- Combines Naive Bayes and Decision Tree algorithms
- Analyzes text content for spam indicators
- User-friendly interface
- Real-time analysis
