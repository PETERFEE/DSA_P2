console.log("✅ content.js loaded in Gmail!");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractEmail") {
    const emailDiv =
      document.querySelector('div[role="main"] div.a3s') ||
      document.querySelector('div[role="main"]');

    if (!emailDiv) {
      console.warn("❌ No email body found.");
      sendResponse({ success: false, text: "" });
      return true;
    }

    let text = emailDiv.innerText || "";
    text = text.replace(/[^\x09\x0A\x0D\x20-\x7E\u00A0-\x00FF]/g, "");
    text = text.replace(/\s{3,}/g, "\n\n").trim();

    console.log("✅ Extracted email text length:", text.length);
    sendResponse({ success: true, text });
    return true;
  }
});
