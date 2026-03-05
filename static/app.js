// LinkedIn Enricher - Frontend JavaScript
console.log("App loaded");

// State
let workflowState = {
    isRunning: false,
    results: null,
};

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));

    const tab = document.getElementById(tabName);
    if (tab) tab.classList.add('active');

    // Find and activate the corresponding button
    const buttons = document.querySelectorAll('.tab-button');
    if (tabName === 'input') buttons[0].classList.add('active');
    else if (tabName === 'progress') buttons[1].classList.add('active');
    else if (tabName === 'results') buttons[2].classList.add('active');
    
    console.log(`Switched to ${tabName} tab`);
}

// Set time window
function setTimeWindow(days) {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);

    document.getElementById('startDate').valueAsDate = startDate;
    document.getElementById('endDate').valueAsDate = endDate;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM ready");

    // Set default dates
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 14);

    document.getElementById('startDate').valueAsDate = startDate;
    document.getElementById('endDate').valueAsDate = endDate;

    // Set first tab active
    document.querySelectorAll('.tab-button')[0].classList.add('active');
    document.querySelectorAll('.tab-content')[0].classList.add('active');

    // Form submission
    const form = document.getElementById('enrichmentForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // Slack checkbox
    const notifCheckbox = document.getElementById('enableNotifications');
    if (notifCheckbox) {
        notifCheckbox.addEventListener('change', function() {
            document.getElementById('slackWebhook').style.display =
                this.checked ? 'block' : 'none';
        });
    }
});

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();

    const companyUrlsElement = document.getElementById('companyUrls');
    const keywordsElement = document.getElementById('keywords');

    console.log('Form submitted - raw values:');
    console.log('Company URLs element exists:', !!companyUrlsElement);
    console.log('Keywords element exists:', !!keywordsElement);
    console.log('Company URLs value:', companyUrlsElement ? companyUrlsElement.value : 'ELEMENT NOT FOUND');
    console.log('Keywords value:', keywordsElement ? keywordsElement.value : 'ELEMENT NOT FOUND');

    const companyUrls = (companyUrlsElement ? companyUrlsElement.value : '')
        .split('\n')
        .map(url => url.trim())
        .filter(url => url);

    const keywords = (keywordsElement ? keywordsElement.value : '')
        .split('\n')
        .map(kw => kw.trim())
        .filter(kw => kw);

    console.log('Parsed company URLs:', companyUrls);
    console.log('Parsed keywords:', keywords);

    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const enableNotifications = document.getElementById('enableNotifications').checked;
    const slackWebhook = document.getElementById('slackWebhook').value;

    console.log('Start date:', startDate, 'End date:', endDate);

    // Validation
    if (!companyUrls.length && !keywords.length) {
        console.error('Validation failed: no company URLs or keywords');
        showError('Please enter at least one company URL or keyword');
        return;
    }

    if (!startDate || !endDate) {
        showError('Please select a date range');
        return;
    }

    const requestData = {
        company_urls: companyUrls,
        keywords: keywords,
        start_date: startDate,
        end_date: endDate,
        enable_notifications: enableNotifications,
        slack_webhook_url: slackWebhook,
    };

    try {
        const submitBtn = document.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Starting...';

        console.log('Sending enrichment request:', requestData);
        
        const response = await fetch('/api/start-enrichment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Failed to start enrichment');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Start Enrichment';
            return;
        }

        console.log('Workflow started:', data);
        
        workflowState.isRunning = true;

        // Switch to progress tab
        switchTab('progress');
        
        // Reset progress displays
        resetProgressDisplays();

        showStatus('Enrichment started! Processing your data...');

        // Start polling
        setTimeout(() => pollStatus(), 500);

    } catch (error) {
        showError('Error: ' + error.message);
        const submitBtn = document.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Start Enrichment';
    }
}

// Reset progress displays
function resetProgressDisplays() {
    document.getElementById('postsCount').textContent = '0';
    document.getElementById('engagementsCount').textContent = '0';
    document.getElementById('peopleCount').textContent = '0';
    
    document.getElementById('companyStatus').textContent = 'Waiting...';
    document.getElementById('keywordStatus').textContent = 'Waiting...';
    document.getElementById('engagementStatus').textContent = 'Waiting...';
    document.getElementById('enrichmentStatus').textContent = 'Waiting...';
}

// Poll for status
async function pollStatus() {
    if (!workflowState.isRunning) {
        console.log('Workflow not running, stopping polls');
        return;
    }

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        console.log('Status poll result:', data);

        if (data.status === 'processing') {
            // Update stats
            if (data.stats) {
                document.getElementById('postsCount').textContent = data.stats.posts_found || 0;
                document.getElementById('engagementsCount').textContent = data.stats.engagements_found || 0;
                document.getElementById('peopleCount').textContent = data.stats.people_enriched || 0;
                
                console.log('Updated stats:', {
                    posts: data.stats.posts_found,
                    engagements: data.stats.engagements_found,
                    people: data.stats.people_enriched
                });
            }
            
            // Poll again after 1 second
            setTimeout(() => pollStatus(), 1000);
            
        } else if (data.status === 'completed') {
            console.log('Workflow completed:', data);
            workflowState.isRunning = false;
            
            // Update final stats
            document.getElementById('postsCount').textContent = data.total_posts || 0;
            document.getElementById('engagementsCount').textContent = data.total_engagements || 0;
            document.getElementById('peopleCount').textContent = data.unique_people || 0;
            
            showStatus('✓ Enrichment completed successfully!');

            // Switch to results tab after 1 second
            setTimeout(function() {
                console.log('Switching to results tab');
                switchTab('results');
                showResultsUI();
            }, 1000);
            
        } else if (data.status === 'failed') {
            workflowState.isRunning = false;
            showError('❌ Enrichment failed: ' + (data.error || 'Unknown error'));
            console.error('Workflow failed:', data.error);
        } else if (data.status === 'idle') {
            // Workflow hasn't started yet, keep polling
            console.log('Workflow idle, polling again...');
            setTimeout(() => pollStatus(), 500);
        } else {
            console.log('Unknown status:', data.status);
            setTimeout(() => pollStatus(), 1000);
        }
    } catch (error) {
        console.error('Error polling status:', error);
        if (workflowState.isRunning) {
            setTimeout(() => pollStatus(), 2000);
        }
    }
}

// Show results UI
function showResultsUI() {
    const resultsContainer = document.getElementById('results');
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }
    
    resultsContainer.innerHTML = `
        <div class="results-container">
            <h3>📊 Export & Filter Results</h3>
            
            <div class="form-section">
                <h4>Download Options</h4>
                <div class="export-buttons">
                    <button class="btn-export" onclick="exportData('csv')">
                        📥 Download as CSV
                    </button>
                    <button class="btn-export" onclick="exportData('excel')">
                        📊 Download as Excel
                    </button>
                    <button class="btn-export" onclick="exportData('json')">
                        {} Download as JSON
                    </button>
                </div>
            </div>
            
            <div class="form-section">
                <button class="btn-secondary" onclick="resetWorkflow()">
                    🔄 Reset & Start Over
                </button>
            </div>
        </div>
    `;
    
    console.log('Results UI displayed');
}

// Export data
async function exportData(format) {
    try {
        console.log('Exporting data as:', format);
        
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: format }),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Failed to export data');
            return;
        }

        // Trigger download
        const link = document.createElement('a');
        link.href = data.download_url;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showStatus('✓ Downloaded: ' + format.toUpperCase());

    } catch (error) {
        showError('Export error: ' + error.message);
    }
}

// Reset workflow
async function resetWorkflow() {
    if (confirm('Reset? All progress will be lost.')) {
        try {
            await fetch('/api/reset', { method: 'POST' });
            workflowState = { isRunning: false, results: null };

            switchTab('input');
            document.getElementById('enrichmentForm').reset();

            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(endDate.getDate() - 14);
            document.getElementById('startDate').valueAsDate = startDate;
            document.getElementById('endDate').valueAsDate = endDate;

            const submitBtn = document.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Start Enrichment';

            showStatus('✓ Workflow reset. Ready for new enrichment.');

        } catch (error) {
            showError('Reset error: ' + error.message);
        }
    }
}

// Helpers
function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        console.error('Error shown:', message);
    }
    console.error(message);
}

function showStatus(message) {
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.style.display = 'block';
        console.log('Status shown:', message);
    }
    console.log(message);
}
