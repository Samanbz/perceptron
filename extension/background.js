// Background service worker
const BACKEND_URL = 'http://localhost:8000';

console.log('Perceptron Scout: Background worker started');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyzeContent') {
        analyzeContent(request.data)
            .then(result => {
                sendResponse({ success: true, result: result });

                // Update badge with relevance indicator
                if (result.relevance_score > 0.5) {
                    chrome.action.setBadgeText({
                        text: Math.round(result.relevance_score * 100).toString(),
                        tabId: sender.tab.id
                    });
                    chrome.action.setBadgeBackgroundColor({
                        color: getTeamColor(result.team),
                        tabId: sender.tab.id
                    });
                }
            })
            .catch(error => {
                console.error('Analysis error:', error);
                sendResponse({ success: false, error: error.message });
            });

        return true; // Keep channel open for async response
    }
});

async function analyzeContent(content) {
    try {
        // Get user token from storage
        const { userToken } = await chrome.storage.local.get(['userToken']);

        const response = await fetch(`${BACKEND_URL}/api/scout/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(userToken && { 'Authorization': `Bearer ${userToken}` })
            },
            body: JSON.stringify(content)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        // Cache result
        const cacheKey = `analysis_${content.url}`;
        await chrome.storage.local.set({
            [cacheKey]: {
                ...result,
                cached_at: new Date().toISOString()
            }
        });

        return result;
    } catch (error) {
        console.error('Failed to analyze content:', error);
        throw error;
    }
}

function getTeamColor(team) {
    const colors = {
        regulator: '#DC2626',
        investor: '#059669',
        competitor: '#7C3AED',
        researcher: '#2563EB'
    };
    return colors[team] || '#667eea';
}

// Clear old cache periodically (every hour)
setInterval(async() => {
    const items = await chrome.storage.local.get(null);
    const oneHourAgo = Date.now() - (60 * 60 * 1000);

    for (const [key, value] of Object.entries(items)) {
        if (key.startsWith('analysis_') && value.cached_at) {
            if (new Date(value.cached_at).getTime() < oneHourAgo) {
                await chrome.storage.local.remove(key);
            }
        }
    }
}, 60 * 60 * 1000);