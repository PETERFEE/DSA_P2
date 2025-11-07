

// popup.js
// This script responds to user action in popup window
// It extracts text from an open Gmail email, computes a spam score

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

    // If not Gmail, show message and exit
    if (!tab || !tab.url || !tab.url.startsWith("https://mail.google.com/")) {
      showMessage("Open an email on mail.google.com and try again.");
      resetButton();
      return;
    }

    // Extract body text
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

    // Handle extraction results
    const injectionResult = injections && injections[0] && injections[0].result;
    if (!injectionResult || !injectionResult.success) {
      const reason = (injectionResult && injectionResult.message) || "Could not extract email text.";
      showMessage(reason);
      resetButton();
      return;
    }

    const cleanedText = injectionResult.cleaned || "";
    lastExtractedText = cleanedText;

    // Default spam score calculation
    const spamResult = computeSpamScore(cleanedText);

    // Show success message with preview and algorithm options
    showMessage(`Preview ready. Spam score: ${spamResult.score}`, true);
    resetButton();
  });


  // Helper: re-enable button after scan
  function resetButton() {
    scanButton.disabled = false;
    scanButton.textContent = "Scan Current Email";
  }

  // Placeholder spam score function
  function computeSpamScore(text) {
    return { score: 0, details: [] };
  }


  // 1. Triple Pass algorithm
  function computeTriplePassScore(text) {
return 0;
  }

  // 2. The Tree algorithm
  function computeTreeScore(text) {
   return 0; 
  }

  // ------------------------------------

  // Display result message in popup
  function showMessage(msg, includePreviewBtn = false) {
    resultDiv.style.display = 'block';
    resultDiv.className = '';
    resultDiv.innerHTML = '';

    const messageDiv = document.createElement('div');
    messageDiv.textContent = msg;
    resultDiv.appendChild(messageDiv);

    // Optionally include preview button + algorithm buttons
    if (includePreviewBtn) {
      const previewBtn = document.createElement('button');
      previewBtn.textContent = "View Preview";
      previewBtn.style.marginTop = "10px";
      previewBtn.addEventListener('click', () => {
        if (lastExtractedText) openPreviewWindow(lastExtractedText);
      });
      resultDiv.appendChild(previewBtn);

      // Add the two new buttons
      triplePassBtn.addEventListener('click', () => {
        if (lastExtractedText) {
          const result = computeTriplePassScore(lastExtractedText);
          showMessage(`Triple Pass Score: ${result.score}`, true);
        }
      });
      treeBtn.addEventListener('click', () => {
        if (lastExtractedText) {
          const result = computeTreeScore(lastExtractedText);
          showMessage(`The Tree Score: ${result.score}`, true);
        }
      });

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





  
  // Escape HTML entities for safe preview
  function escapeHtml(s) {
    if (!s) return "";
    return s.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
  }
});
