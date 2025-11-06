chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  const emailDiv = document.querySelector('div[role="main"] div.a3s') 
                || document.querySelector('div[role="main"]');
  if (!emailDiv) {
    sendResponse({ success: false, message: "Please open an email first." });
    return;
  }

  // Extract raw text
  let text = emailDiv.innerText || "";
  
  // 🧹 Clean: remove weird characters (non-printable or garbled)
  // Keeps: letters, numbers, punctuation, and whitespace
  text = text.replace(/[^\x09\x0A\x0D\x20-\x7E\u00A0-\u00FF]/g, "");

  // Remove excessive newlines/spaces
  text = text.replace(/\s{3,}/g, "\n\n").trim();

  // --- Preview Email ---
  if (req.action === "previewEmail") {
    const html = `
      <html><head><title>Email Preview</title></head>
      <body style="font-family:sans-serif;max-width:800px;margin:auto;padding:20px;white-space:pre-wrap">
        <h2>Email Body Preview</h2>
        <pre>${text}</pre>
      </body></html>`;
    const url = URL.createObjectURL(new Blob([html], { type: "text/html" }));
    sendResponse({ success: true, previewUrl: url });
    return;
  }

  // --- Scan Email ---
  if (req.action === "scanEmail") {
    const spamWords = ["winner", "prize", "click here", "urgent", "free", "offer", "guaranteed"];
    const found = spamWords.filter(word => text.toLowerCase().includes(word));
    const isSpam = found.length > 1;

    sendResponse({
      isSpam,
      reason: isSpam
        ? `SPAM RISK: Found ${found.slice(0, 3).join(", ")}`
        : "Looks safe. No common spam words found."
    });
  }
});
