document.addEventListener('DOMContentLoaded', () => {
  const scanButton = document.getElementById('scanButton');
  const resultDiv = document.getElementById('result');

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

  async function previewEmail() {
    try {
      let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (tab.url && tab.url.startsWith("https://mail.google.com/")) {
        const response = await chrome.tabs.sendMessage(tab.id, { action: "previewEmail" });
        
        if (response && response.success) {
          // Open the preview URL in a new window
          window.open(response.previewUrl, 'emailPreview', 'width=800,height=600');
        } else {
          alert(response.message || "Could not preview email. Make sure an email is open.");
        }
      }
    } catch (error) {
      console.error("Error previewing email:", error);
      alert("Could not preview email. Make sure an email is fully open.");
    }
  }

  function displayResult(response) {
    resultDiv.style.display = 'block';
    
    // Clear previous content and classes
    resultDiv.innerHTML = '';
    resultDiv.className = '';
    
    // Create and append the result message
    const messageDiv = document.createElement('div');
    messageDiv.textContent = response.reason;
    resultDiv.appendChild(messageDiv);
    
    // Add appropriate class based on scan result
    if (response.isSpam) {
      resultDiv.classList.add('spam');
    } else if (response.reason.startsWith("Looks safe")) {
      resultDiv.classList.add('safe');
    }
    
    // Add Preview button if we successfully found an email
    if (!response.reason.includes("Could not find email")) {
      const previewButton = document.createElement('button');
      previewButton.textContent = "Preview Email Body";
      previewButton.className = 'preview-button';
      previewButton.onclick = previewEmail;
      
      // Add some spacing
      const spacer = document.createElement('div');
      spacer.style.height = '10px';
      
      resultDiv.appendChild(spacer);
      resultDiv.appendChild(previewButton);
    }
  }
});
