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
document.getElementById('scanButton').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab || !tab.url.startsWith("https://mail.google.com/")) {
    alert("Please open an email in Gmail first.");
    return;
  }

  // Inject getCleanedEmailBody into Gmail page
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: getCleanedEmailBody,
  });

  if (!result) {
    alert("Could not extract email body.");
    return;
  }

  // Now analyze the extracted text
  analyzeEmailText(result);
});

// Function runs inside Gmail tab context
function getCleanedEmailBody() {
  const emailDiv =
    document.querySelector('div[role="main"] div.a3s') ||
    document.querySelector('div[role="main"]');

  if (!emailDiv) return "";

  let text = emailDiv.innerText || "";
  text = text.replace(/[^\x09\x0A\x0D\x20-\x7E\u00A0-\u00FF]/g, "");
  text = text.replace(/\s{3,}/g, "\n\n").trim();
  return text;
}