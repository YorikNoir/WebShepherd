// WebShepherd Frontend App

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8001/api'
    : '/webshepherd/api';

// DOM Elements
const scanForm = document.getElementById('scan-form');
const urlInput = document.getElementById('url-input');
const scanBtn = document.getElementById('scan-btn');
const errorMessage = document.getElementById('error-message');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const newScanBtn = document.getElementById('new-scan-btn');

// Results Elements
const scoreValue = document.getElementById('score-value');
const scoreCircle = document.getElementById('score-circle');
const resultUrl = document.getElementById('result-url');
const passCount = document.getElementById('pass-count');
const warningCount = document.getElementById('warning-count');
const failCount = document.getElementById('fail-count');
const scanTime = document.getElementById('scan-time');
const principlesSummary = document.getElementById('principles-summary');
const findingsContainer = document.getElementById('findings-container');

// Event Listeners
scanForm.addEventListener('submit', handleScanSubmit);
newScanBtn.addEventListener('click', resetForm);

// Handle form submission
async function handleScanSubmit(e) {
    e.preventDefault();

    const url = urlInput.value.trim();

    if (!url) {
        showError('Please enter a URL');
        return;
    }

    // Validate URL format
    if (!isValidUrl(url)) {
        showError('Please enter a valid URL (e.g., https://example.com)');
        return;
    }

    hideError();
    await performScan(url);
}

// Perform accessibility scan
async function performScan(url) {
    showLoading();

    try {
        // Submit scan request
        const response = await fetch(`${API_BASE_URL}/scan/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to scan URL');
        }

        const scanData = await response.json();

        // Poll for results
        await pollScanResults(scanData.id);

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Poll for scan results
async function pollScanResults(scanId, attempts = 0) {
    const maxAttempts = 30; // 30 seconds max

    if (attempts >= maxAttempts) {
        hideLoading();
        showError('Scan timeout. Please try again.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/scan/${scanId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch scan results');
        }

        const scanData = await response.json();

        if (scanData.status === 'completed') {
            hideLoading();
            displayResults(scanData);
        } else if (scanData.status === 'failed') {
            hideLoading();
            showError(scanData.error || 'Scan failed');
        } else {
            // Still processing, poll again
            setTimeout(() => pollScanResults(scanId, attempts + 1), 1000);
        }

    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Display scan results
function displayResults(scanData) {
    // Update score
    const score = Math.round(scanData.score);
    scoreValue.textContent = score;

    // Update score circle color based on score
    if (score >= 80) {
        scoreCircle.style.borderColor = 'var(--success)';
        scoreValue.style.color = 'var(--success)';
    } else if (score >= 50) {
        scoreCircle.style.borderColor = 'var(--warning)';
        scoreValue.style.color = 'var(--warning)';
    } else {
        scoreCircle.style.borderColor = 'var(--danger)';
        scoreValue.style.color = 'var(--danger)';
    }

    // Update URL and stats
    resultUrl.textContent = scanData.url;
    passCount.textContent = scanData.passed;
    warningCount.textContent = scanData.warnings;
    failCount.textContent = scanData.failed;

    // Format scan time
    const scanDate = new Date(scanData.created_at);
    scanTime.textContent = `Scanned: ${scanDate.toLocaleString()}`;

    // Update principles summary
    const principlesData = groupByPrinciple(scanData.findings);
    displayPrinciples(principlesData);

    // Display findings
    displayFindings(scanData.findings);

    // Show results section
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Group findings by WCAG principle
function groupByPrinciple(findings) {
    const principles = {
        'Perceivable': { findings: [], issues: 0 },
        'Operable': { findings: [], issues: 0 },
        'Understandable': { findings: [], issues: 0 },
        'Robust': { findings: [], issues: 0 }
    };

    findings.forEach(finding => {
        const principle = finding.principle;
        if (principles[principle]) {
            principles[principle].findings.push(finding);
            if (finding.status !== 'pass') {
                principles[principle].issues++;
            }
        }
    });

    return principles;
}

// Display principles summary
function displayPrinciples(principlesData) {
    principlesSummary.innerHTML = '';

    Object.entries(principlesData).forEach(([name, data]) => {
        const card = document.createElement('div');
        card.className = 'principle-card';

        const issueText = data.issues === 0
            ? 'No issues found'
            : `${data.issues} issue${data.issues !== 1 ? 's' : ''} found`;

        card.innerHTML = `
            <h4>${name}</h4>
            <p class="issue-count">${issueText}</p>
        `;

        principlesSummary.appendChild(card);
    });
}

// Display findings
function displayFindings(findings) {
    findingsContainer.innerHTML = '';

    if (findings.length === 0) {
        findingsContainer.innerHTML = '<p>No findings to display.</p>';
        return;
    }

    findings.forEach(finding => {
        const findingEl = document.createElement('div');
        findingEl.className = `finding ${finding.status}`;

        // Status icon
        const statusIcon = finding.status === 'pass' ? '✓' : finding.status === 'warning' ? '⚠' : '✗';

        // Build element preview
        let elementPreview = '';
        if (finding.element) {
            const truncated = finding.element.length > 200
                ? finding.element.substring(0, 200) + '...'
                : finding.element;
            elementPreview = `<div class="finding-element">${escapeHtml(truncated)}</div>`;
        }

        // Build remediation
        let remediationHtml = '';
        if (finding.remediation) {
            remediationHtml = `
                <div class="finding-remediation">
                    <strong>How to fix:</strong>
                    ${escapeHtml(finding.remediation)}
                </div>
            `;
        }

        findingEl.innerHTML = `
            <div class="finding-header">
                <div>
                    <div class="finding-title">${statusIcon} ${escapeHtml(finding.rule_name)}</div>
                    <div class="finding-meta">
                        <span>Level: ${escapeHtml(finding.level)}</span>
                        <span>Principle: ${escapeHtml(finding.principle)}</span>
                        <span>Guideline: ${escapeHtml(finding.guideline)}</span>
                    </div>
                </div>
            </div>
            <div class="finding-message">${escapeHtml(finding.message)}</div>
            ${remediationHtml}
            ${elementPreview}
        `;

        findingsContainer.appendChild(findingEl);
    });
}

// Reset form for new scan
function resetForm() {
    scanForm.reset();
    resultsSection.classList.add('hidden');
    hideError();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show loading state
function showLoading() {
    scanForm.classList.add('hidden');
    loadingSection.classList.remove('hidden');
}

// Hide loading state
function hideLoading() {
    loadingSection.classList.add('hidden');
    scanForm.classList.remove('hidden');
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Hide error message
function hideError() {
    errorMessage.classList.add('hidden');
}

// Validate URL format
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
