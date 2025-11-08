// Popup script
document.addEventListener('DOMContentLoaded', async() => {
    const scoutToggle = document.getElementById('scoutToggle');
    const statusText = document.getElementById('statusText');
    const scanButton = document.getElementById('scanButton');
    const dashboardButton = document.getElementById('dashboardButton');
    const currentPageStats = document.getElementById('currentPageStats');
    const loadingMessage = document.getElementById('loadingMessage');
    const errorMessage = document.getElementById('errorMessage');

    // Load saved state
    const { scoutingEnabled } = await chrome.storage.local.get(['scoutingEnabled']);
    scoutToggle.checked = scoutingEnabled !== false;
    updateStatus(scoutToggle.checked);

    // Toggle scouting mode
    scoutToggle.addEventListener('change', async(e) => {
        const enabled = e.target.checked;
        await chrome.storage.local.set({ scoutingEnabled: enabled });
        updateStatus(enabled);

        // Notify content script
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, {
            action: 'toggleScouting',
            enabled: enabled
        });
    });

    // Scan current page
    scanButton.addEventListener('click', async() => {
        loadingMessage.style.display = 'block';
        errorMessage.style.display = 'none';
        currentPageStats.style.display = 'none';

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            chrome.tabs.sendMessage(tab.id, { action: 'scanNow' }, async(response) => {
                if (response && response.success) {
                    // Check for cached analysis
                    const cacheKey = `analysis_${tab.url}`;
                    const cached = await chrome.storage.local.get([cacheKey]);

                    if (cached[cacheKey]) {
                        displayAnalysis(cached[cacheKey]);
                    } else {
                        setTimeout(async() => {
                            const updated = await chrome.storage.local.get([cacheKey]);
                            if (updated[cacheKey]) {
                                displayAnalysis(updated[cacheKey]);
                            } else {
                                loadingMessage.textContent = 'Still processing...';
                            }
                        }, 2000);
                    }
                } else {
                    showError('Failed to scan page');
                }
            });
        } catch (error) {
            showError(error.message);
        }
    });

    // Open dashboard
    dashboardButton.addEventListener('click', () => {
        chrome.tabs.create({ url: 'http://localhost:5173/dashboard' });
    });

    // Check for current page analysis
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
        const cacheKey = `analysis_${tab.url}`;
        const cached = await chrome.storage.local.get([cacheKey]);
        if (cached[cacheKey]) {
            displayAnalysis(cached[cacheKey]);
        }
    }

    function updateStatus(enabled) {
        if (enabled) {
            statusText.textContent = 'Active · Analyzing pages';
            statusText.style.color = '#059669';
        } else {
            statusText.textContent = 'Paused · Not analyzing';
            statusText.style.color = '#DC2626';
        }
    }

    function displayAnalysis(analysis) {
        loadingMessage.style.display = 'none';
        currentPageStats.style.display = 'block';

        // Update relevance score
        const relevancePercent = Math.round((analysis.relevance_score || 0) * 100);
        document.getElementById('relevanceScore').textContent = `${relevancePercent}%`;

        // Update team badge
        const teamBadge = document.getElementById('teamBadge');
        if (analysis.team) {
            teamBadge.innerHTML = `<span class="team-badge team-${analysis.team}">${analysis.team}</span>`;
        } else {
            teamBadge.textContent = 'None';
        }

        // Update keyword count
        const keywordCount = analysis.top_keywords ? analysis.top_keywords.length : 0;
        document.getElementById('keywordCount').textContent = keywordCount;
    }

    function showError(message) {
        loadingMessage.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.textContent = `Error: ${message}`;
    }
});