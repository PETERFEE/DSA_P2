// popup.js
// This script responds to user action in popup window
// It extracts text from an open Gmail email, computes a spam score via Flask server

document.addEventListener('DOMContentLoaded', () => {

  const scanButton = document.getElementById('scanButton');
  const resultDiv = document.getElementById('result');
  let lastExtractedText = "";

  // -triple Pass and The Tree buttons
  const triplePassBtn = document.createElement('button');
  triplePassBtn.textContent = "Triple Pass";
  triplePassBtn.style.marginTop = "8px";

  const treeBtn = document.createElement('button');
  treeBtn.textContent = "The Tree";
  treeBtn.style.marginTop = "8px";
  // --------------------

  // When user clicks "Scan Current Email"
  scanButton.addEventListener('click', async () => {
    scanButton.disabled = true;
    scanButton.textContent = "Extracting...";
    resultDiv.style.display = 'none';
    resultDiv.className = '';
    resultDiv.innerHTML = '';

    // Get current active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url || !tab.url.startsWith("https://mail.google.com/")) {
      showMessage("Open an email on mail.google.com and try again.");
      resetButton();
      return;
    }

    // Extract body text from Gmail
    const injections = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const emailDiv = document.querySelector('div[role="main"] div.a3s')
                      || document.querySelector('div[role="main"]');
        if (!emailDiv) {
          return { success: false, message: "Could not find an open email. Make sure an email is selected." };
        }
        let text = emailDiv.innerText || "";
        text = text.replace(/[^\x09\x0A\x0D\x20-\x7E\u00A0-\u00FF]/g, "");
        text = text.replace(/\s{3,}/g, "\n\n").trim();
        return { success: true, cleaned: text };
      },
    });

    const injectionResult = injections && injections[0] && injections[0].result;
    if (!injectionResult || !injectionResult.success) {
      const reason = (injectionResult && injectionResult.message) || "Could not extract email text.";
      showMessage(reason);
      resetButton();
      return;
    }

    const cleanedText = injectionResult.cleaned || "";
    lastExtractedText = cleanedText;

    // --- Call Flask server ---
    try {
      const response = await fetch('http://127.0.0.1:5000/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: cleanedText,
          nb_conf: 0.5,  // default confidence
          has_name: cleanedText.includes("Hi") // simple heuristic
        })
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const result = await response.json();

      showMessage(`Preview ready. Spam score: ${result.spam_score}`, true);
      resetButton();
    } catch (error) {
      console.error('Fetch Error:', error);
      showMessage('Error: Could not connect to Flask server. Make sure server is running.');
      resetButton();
    }
  });

  function resetButton() {
    scanButton.disabled = false;
    scanButton.textContent = "Scan Current Email";
  }

  // Display result message in popup
  function showMessage(msg, includePreviewBtn = false) {
    resultDiv.style.display = 'block';
    resultDiv.className = '';
    resultDiv.innerHTML = '';

    const messageDiv = document.createElement('div');
    messageDiv.textContent = msg;
    resultDiv.appendChild(messageDiv);

    if (includePreviewBtn) {
      const previewBtn = document.createElement('button');
      previewBtn.textContent = "View Preview";
      previewBtn.style.marginTop = "10px";
      previewBtn.addEventListener('click', () => {
        if (lastExtractedText) openPreviewWindow(lastExtractedText);
      });
      resultDiv.appendChild(previewBtn);

      resultDiv.appendChild(triplePassBtn);
      resultDiv.appendChild(treeBtn);
    }
  }

  // Open new window to show extracted email text
  function openPreviewWindow(text) {
    const html = `
      <!doctype html>
      <html>
        <head>
          <meta charset="utf-8">
          <title>Email Preview</title>
          <style>
            body { font-family: sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
            pre { white-space: pre-wrap; word-wrap: break-word; background:#f7f7f7; padding:16px; border-radius:6px; }
          </style>
        </head>
        <body>
          <h2>Email Body Preview</h2>
          <pre>${escapeHtml(text)}</pre>
        </body>
      </html>`;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    window.open(url, 'emailPreview', 'width=900,height=700');
  }

  function escapeHtml(s) {
    if (!s) return "";
    return s.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
  }
});
