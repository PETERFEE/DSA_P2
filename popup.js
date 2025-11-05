document.addEventListener('DOMContentLoaded', () => {
  const scanButton = document.getElementById('scanButton');
  const resultDiv = document.getElementById('result');
  const previewBodyButton = document.getElementById('previewBodyButton');
  // Hide preview button by default; show after a scan
  previewBodyButton.style.display = 'none';

  previewBodyButton.addEventListener('click', async () => {
    previewBodyButton.disabled = true;
    previewBodyButton.textContent = "Loading...";
    try {
      let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab.url && tab.url.startsWith("https://mail.google.com/")) {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
        // Ask content script for just the body
        const response = await chrome.tabs.sendMessage(tab.id, { action: "extractBodyOnly" });
        if (response && response.body) {
          const blob = new Blob([
            `<html><head><title>Email Body Preview</title></head><body style='font-family:sans-serif;white-space:pre-wrap;padding:2em;'><h2>Email Body</h2><div>${response.body.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div></body></html>`
          ], { type: 'text/html' });
          const url = URL.createObjectURL(blob);
          chrome.tabs.create({ url });
        } else {
          alert('Could not extract email body.');
        }
      } else {
        alert('Please open an email on mail.google.com to use this.');
      }
    } catch (e) {
      alert('Error extracting body: ' + e.message);
    } finally {
      previewBodyButton.disabled = false;
      previewBodyButton.textContent = "Preview Body in New Tab";
    }
  });

  scanButton.addEventListener('click', async () => {
    // Disable button and show loading
    scanButton.disabled = true;
    scanButton.textContent = "Scanning...";
    resultDiv.style.display = 'none';
    resultDiv.className = '';

    try {
      // Get the current active tab
      let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

      // Check if we are on a Gmail page
      if (tab.url && tab.url.startsWith("https://mail.google.com/")) {
        
        // Inject the content script into the page
        // This is necessary to be able to read the page's content
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });

        // Send a message to the injected content script
        const response = await chrome.tabs.sendMessage(tab.id, { action: "scanEmail" });

  // Display the response from the content script
  displayResult(response);

  // Reveal the preview button now that a scan was performed
  previewBodyButton.style.display = 'block';

      } else {
        // Not on Gmail
        displayResult({ isSpam: false, reason: "Please open an email on mail.google.com to use this." });
      }

    } catch (error) {
      console.error("Error during scan:", error);
      displayResult({ isSpam: false, reason: "Could not scan email. Make sure an email is fully open and try again." });
    } finally {
      // Re-enable the button
      scanButton.disabled = false;
      scanButton.textContent = "Scan Current Email";
    }
  });

  function displayResult(response) {
    resultDiv.style.display = 'block';
    resultDiv.textContent = response.reason;
    if (response.isSpam) {
      resultDiv.classList.add('spam');
    } else if (response.reason.startsWith("Looks safe")) {
      resultDiv.classList.add('safe');
    }
  }
});
