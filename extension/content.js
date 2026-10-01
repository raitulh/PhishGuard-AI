chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => { if (message.type === 'VISIBLE_TEXT') { sendResponse(document.body?.innerText?.slice(0, 12000) || ''); } return true; });
