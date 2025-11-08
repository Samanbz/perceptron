// Content extraction script - runs on every page
console.log('Perceptron Scout: Content script loaded');

let scoutingEnabled = true;
let lastScannedUrl = '';

// Listen for messages from web app
window.addEventListener('message', (event) => {
    // Check extension status request from web app
    if (event.data.type === 'CHECK_EXTENSION') {
        chrome.storage.local.get(['scoutingEnabled'], (result) => {
            window.postMessage({
                type: 'EXTENSION_INSTALLED',
                scoutingEnabled: result.scoutingEnabled !== false
            }, '*');
        });
    }

    // Toggle scouting from web app
    if (event.data.type === 'TOGGLE_SCOUTING') {
        scoutingEnabled = event.data.enabled;
        chrome.storage.local.set({ scoutingEnabled: event.data.enabled });

        // Send acknowledgment
        window.postMessage({
            type: 'SCOUTING_TOGGLED',
            enabled: event.data.enabled
        }, '*');
    }
});

// Check if scouting is enabled
chrome.storage.local.get(['scoutingEnabled'], (result) => {
    scoutingEnabled = result.scoutingEnabled !== false;
    if (scoutingEnabled && window.location.href !== lastScannedUrl) {
        setTimeout(extractAndAnalyze, 2000); // Wait 2s for page to load
    }
});

function extractAndAnalyze() {
    const currentUrl = window.location.href;

    // Skip certain URLs
    if (currentUrl.includes('chrome://') ||
        currentUrl.includes('chrome-extension://') ||
        currentUrl.includes('about:') ||
        currentUrl === lastScannedUrl) {
        return;
    }

    lastScannedUrl = currentUrl;

    // Extract page content
    const content = extractPageContent();

    // Send to background script
    chrome.runtime.sendMessage({
        action: 'analyzeContent',
        data: content
    }, (response) => {
        if (response && response.success) {
            console.log('Perceptron: Page analyzed', response.result);
            showNotification(response.result);
        }
    });
}

function extractPageContent() {
    // Get page title
    const title = document.title || '';

    // Get meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    const description = metaDesc ? metaDesc.content : '';

    // Get main content (try multiple selectors)
    let mainContent = '';

    // Try to find main content area
    const mainSelectors = [
        'main',
        'article',
        '[role="main"]',
        '.content',
        '.main-content',
        '#content',
        '#main'
    ];

    for (const selector of mainSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            mainContent = element.innerText;
            break;
        }
    }

    // Fallback to body text
    if (!mainContent) {
        mainContent = document.body.innerText;
    }

    // Limit content length (first 5000 chars)
    mainContent = mainContent.substring(0, 5000);

    // Get all headings for context
    const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
        .map(h => h.innerText.trim())
        .filter(h => h.length > 0)
        .slice(0, 10);

    // Get meta keywords if available
    const metaKeywords = document.querySelector('meta[name="keywords"]');
    const keywords = metaKeywords ? metaKeywords.content : '';

    return {
        url: window.location.href,
        title: title,
        description: description,
        content: mainContent,
        headings: headings,
        keywords: keywords,
        timestamp: new Date().toISOString(),
        domain: window.location.hostname
    };
}

function showNotification(result) {
    if (!result.team || result.relevance_score < 0.3) {
        return; // Don't notify for low relevance
    }

    // Show subtle in-page notification
    const notification = document.createElement('div');
    notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 999999;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
  `;

    const teamColors = {
        regulator: '#DC2626',
        investor: '#059669',
        competitor: '#7C3AED',
        researcher: '#2563EB'
    };

    notification.innerHTML = `
    <div style="font-weight: 600; margin-bottom: 4px;">
      🎯 Perceptron Scout
    </div>
    <div style="font-size: 12px; opacity: 0.9;">
      ${result.team.toUpperCase()} · Relevance: ${Math.round(result.relevance_score * 100)}%
    </div>
  `;

    notification.style.background = teamColors[result.team] || notification.style.background;

    document.body.appendChild(notification);

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(400px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
    document.head.appendChild(style);

    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'toggleScouting') {
        scoutingEnabled = request.enabled;
        sendResponse({ success: true });
    } else if (request.action === 'scanNow') {
        extractAndAnalyze();
        sendResponse({ success: true });
    }
    return true;
});