// popup.js
async function analyzeEmailText(textToAnalyze) {
  const dtSection = document.getElementById('decision-tree-section');
  const rfSection = document.getElementById('rule-filter-section');
  const dtResult = document.getElementById('dt-result');
  const dtReasoning = document.getElementById('dt-reasoning');
  const dtTime = document.getElementById('dt-compile-time');
  const rfResult = document.getElementById('rf-result');
  const rfTime = document.getElementById('rf-compile-time');

  // Reset UI
  dtSection.style.display = "none";
  rfSection.style.display = "none";
  dtResult.textContent = "Analyzing...";
  dtResult.className = "";
  rfResult.textContent = "";
  rfResult.className = "";

  try {
    const response = await fetch('http://127.0.0.1:5000/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: textToAnalyze })
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const result = await response.json();

    // ----- Decision Tree Section -----
    const dt = result.decision_tree;
    dtSection.style.display = "block";
    dtResult.textContent = `Result: ${dt.classification.toUpperCase()} (Score: ${dt.spam_score.toFixed(2)})`;
    dtResult.className = dt.classification === "spam" ? "spam" : "safe";

    // Reasoning
    if (dt.reasoning && dt.reasoning.decision_path) {
      dtReasoning.innerHTML = `<strong>Reasoning:</strong><br>${dt.reasoning.decision_path.map(step => "• " + step).join("<br>")}`;
    } else {
      dtReasoning.textContent = "";
    }

    // Compile time
    dtTime.textContent = `Execution Time: ${(dt.compile_time * 1000).toFixed(2)} ms`;

    // ----- Rule Filter Section -----
    const rf = result.rule_filter;
    rfSection.style.display = "block";
    rfResult.textContent = `Result: ${rf.classification.toUpperCase()} (Score: ${rf.spam_score.toFixed(2)})`;
    rfResult.className = rf.classification.toLowerCase() === "spam" ? "spam" : "safe";
    rfTime.textContent = `Execution Time: ${(rf.compile_time).toFixed(2)} ms`;

  } catch (err) {
    console.error(err);
    dtResult.textContent = "Error connecting to server.";
    dtResult.className = "spam";
  }
}

// Attach click handler
document.getElementById('scanButton').addEventListener('click', () => {
  const textInput = document.getElementById('text-to-check').value.trim();
  analyzeEmailText(textInput);
});
