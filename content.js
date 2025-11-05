// This script runs in the context of the Gmail webpage
// It listens for a message from popup.js

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scanEmail") {
  }

  // Extract only the email body for preview
  if (request.action === "extractBodyOnly") {
    let bodyText = '';
    // Try Gmail's main message body selector first
    const bodyEl = document.querySelector('div.a3s');
    if (bodyEl) {
      bodyText = bodyEl.innerText.trim();
    } else {
      // fallback to main area
      const mainEl = document.querySelector('div[role="main"]');
      bodyText = mainEl ? mainEl.innerText.trim() : '';
    }
    sendResponse({ body: bodyText });
    return true;
    
    // --- This is a simple, example-only spam detection ---
    // --- Real spam detection is far more complex! ---

    const spamKeywords = [
      'congratulations', 'winner', 'prize', 'free money', 'click here',
      'limited time offer', 'act now', 'urgent', 'payment required',
      'invoice', 'pharmacy', 'viagra', 'investment', 'guaranteed',
      'dear friend', 'nigerian prince', 'clearance', 'no cost'
    ];

    let emailText = '';

    // Try to find the main element holding the open email.
    // Gmail's HTML structure changes, so this is a best-guess selector.
    // This selector targets the main readable area of an open email.
    const emailBody = document.querySelector('div[role="main"]');

    if (emailBody) {
      emailText = emailBody.innerText.toLowerCase();
    } else {
      // Could not find the email body
      sendResponse({ aws: false, reason: "Could not find email content. Please make sure an email is open." });
      return true; // Indicate async response
    }

    let foundKeywords = [];
    let spamScore = 0;

    for (const keyword of spamKeywords) {
      if (emailText.includes(keyword)) {
        spamScore++;
        foundKeywords.push(keyword);
      }
    }

    // Send the result back to the popup
    if (spamScore > 1) { // If 2 or more keywords are found
      sendResponse({ 
        isSpam: true, 
        reason: `SPAM RISK: Found keywords: ${foundKeywords.slice(0, 3).join(', ')}...` 
      });
    } else {
      sendResponse({ 
        isSpam: false, 
        reason: "Looks safe. No common spam keywords found." 
      });
    }
  }
  
  // Return true to indicate that we will send a response asynchronously
  return true;
});
