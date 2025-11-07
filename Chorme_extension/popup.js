// popup.js
// This function sends email text to Flask server for classification
async function analyzeEmailText(textToAnalyze) {
  const resultElement = document.getElementById('result');
  const reasoningElement = document.getElementById('reasoning');
  const compileTimeElement = document.getElementById('compile-time'); // New element for time

  // Reset UI
  resultElement.style.display = "block";
  reasoningElement.style.display = "none";
  compileTimeElement.style.display = "none";
  resultElement.textContent = "Analyzing...";
  resultElement.className = "";
  compileTimeElement.textContent = "";

  const hasName = /hi\s+\w+/i.test(textToAnalyze);

  try {
    const response = await fetch('http://127.0.0.1:5000/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: textToAnalyze,
        has_name: hasName
      })
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const result = await response.json();

    // Show main classification
    resultElement.textContent = `Result: ${result.classification.toUpperCase()} (Score: ${result.spam_score.toFixed(2)})`;
    resultElement.className = result.classification === "spam" ? "spam" : "safe";

    // Show reasoning if available
    if (result.reasoning) {
      const reasons = [];

      if (result.reasoning.nb_prediction)
        reasons.push(`Naive Bayes says: ${result.reasoning.nb_prediction} (confidence: ${(result.reasoning.nb_confidence * 100).toFixed(1)}%)`);

      if (result.reasoning.decision_path && result.reasoning.decision_path.length > 0)
        reasons.push(...result.reasoning.decision_path.map(step => `• ${step}`));

      if (reasons.length > 0) {
        reasoningElement.innerHTML = `<strong>Reasoning:</strong><br>${reasons.join('<br>')}`;
        reasoningElement.style.display = "block";
      }
    }

    // Show compile time
    if (result.Complie_time !== undefined) {
      compileTimeElement.textContent = `Execution Time: ${(result.Complie_time * 1000).toFixed(2)} ms`;
      compileTimeElement.style.display = "block";
    }

  } catch (err) {
    resultElement.textContent = "Error connecting to server.";
    resultElement.className = "spam";
    console.error(err);
  }
}

// Attach click handler
document.getElementById('scanButton').addEventListener('click', () => {
  const textInput = document.getElementById('text-to-check').value.trim();
  analyzeEmailText(textInput);
});
