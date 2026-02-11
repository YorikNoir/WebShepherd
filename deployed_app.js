// WebShepherd Frontend App

console.log('🐑 WebShepherd initialized');
console.log('🌐 Hostname:', window.location.hostname);
console.log('📍 Current URL:', window.location.href);

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8001/api'
    : '/api';

console.log('⚙️ API Base URL:', API_BASE_URL);

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
const scoreBadge = document.getElementById('score-badge');
const sheepRating = document.getElementById('sheep-rating');
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
    console.log('🚀 Form submitted');

    const url = urlInput.value.trim();
    console.log('📝 URL to scan:', url);

    if (!url) {
        console.warn('⚠️ Empty URL');
        showError('Please enter a URL');
        return;
    }

    // Validate URL format
    if (!isValidUrl(url)) {
        console.warn('⚠️ Invalid URL format:', url);
        showError('Please enter a valid URL (e.g., https://example.com)');
        return;
    }

    console.log('✅ URL validated, starting scan...');
    hideError();
    await performScan(url);
}

// Perform accessibility scan
async function performScan(url) {
    console.log('🔍 Starting scan for:', url);
    console.log('🌐 API Base URL:', API_BASE_URL);
    showLoading();

    try {
        // Submit scan request
        const apiUrl = `${API_BASE_URL}/scan/`;
        console.log('📡 POST request to:', apiUrl);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        console.log('📥 Response status:', response.status, response.statusText);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('❌ API Error:', errorData);
            throw new Error(errorData.detail || 'Failed to scan URL');
        }

        const scanData = await response.json();
        console.log('✅ Scan created:', scanData);
        console.log('🆔 Scan ID:', scanData.scan_id);

        // Poll for results
        await pollScanResults(scanData.scan_id);

    } catch (error) {
        console.error('❌ Scan failed:', error);
        hideLoading();
        showError(error.message);
    }
}

// Poll for scan results
async function pollScanResults(scanId, attempts = 0) {
    const maxAttempts = 30; // 30 seconds max

    console.log(`🔄 Polling attempt ${attempts + 1}/${maxAttempts} for scan ID: ${scanId}`);

    if (attempts >= maxAttempts) {
        console.error('⏱️ Scan timeout after', maxAttempts, 'attempts');
        hideLoading();
        showError('Scan timeout. Please try again.');
        return;
    }

    try {
        const pollUrl = `${API_BASE_URL}/scan/${scanId}`;
        console.log('📡 GET request to:', pollUrl);

        const response = await fetch(pollUrl);
        console.log('📥 Poll response status:', response.status);

        if (!response.ok) {
            console.error('❌ Poll failed with status:', response.status);
            throw new Error('Failed to fetch scan results');
        }

        const scanData = await response.json();
        console.log('📊 Scan data:', scanData);
        console.log('📍 Scan status:', scanData.status);

        if (scanData.status === 'complete') {
            console.log('✅ Scan complete!');
            console.log('📈 Score:', scanData.score);
            console.log('📋 Total findings:', scanData.findings?.length || 0);
            hideLoading();
            displayResults(scanData);
        } else if (scanData.status === 'failed') {
            console.error('❌ Scan failed:', scanData.error);
            hideLoading();
            showError(scanData.error || 'Scan failed');
        } else {
            // Still processing, poll again
            console.log('⏳ Scan still in progress (status:', scanData.status, '), polling again in 1s...');
            setTimeout(() => pollScanResults(scanId, attempts + 1), 1000);
        }

    } catch (error) {
        console.error('❌ Polling error:', error);
        hideLoading();
        showError(error.message);
    }
}

// Display scan results
function displayResults(scanData) {
    console.log('🎨 Displaying results:', scanData);

    // Update score
    const score = Math.round(scanData.score);
    console.log('💯 Final score:', score);

    // Display score number
    scoreValue.textContent = score;

    // Sheep rating based on score!
    let rating = '';
    let badgeClass = '';
    
    if (score >= 90) {
        rating = '🐑🐑🐑 Excellent flock!';
        badgeClass = 'score-excellent';
    } else if (score >= 80) {
        rating = '🐑🐑 Great flock!';
        badgeClass = 'score-great';
    } else if (score >= 60) {
        rating = '🐑 Good flock';
        badgeClass = 'score-good';
    } else if (score >= 40) {
        rating = '🐑🐏 Mixed flock';
        badgeClass = 'score-mixed';
    } else {
        rating = '🐏🐏 Needs shepherding';
        badgeClass = 'score-poor';
    }
    
    sheepRating.textContent = rating;
    scoreBadge.className = `score-badge ${badgeClass}`;

    // Update URL and stats
    resultUrl.textContent = scanData.url;
    passCount.textContent = scanData.passed_checks;
    warningCount.textContent = scanData.warnings;
    failCount.textContent = scanData.failures;

    console.log('📊Stats - Passed:', scanData.passed_checks, 'Warnings:', scanData.warnings, 'Failures:', scanData.failures);

    // Format scan time
    const scanDate = new Date(scanData.created_at);
    scanTime.textContent = `Scanned: ${scanDate.toLocaleString()}`;

    // Update principles summary using backend counts
    updatePrinciplesCounts(
        scanData.perceivable_issues,
        scanData.operable_issues,
        scanData.understandable_issues,
        scanData.robust_issues
    );

    // Display findings
    console.log('🔍 Displaying', scanData.findings?.length || 0, 'findings');
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
            if (finding.severity !== 'pass') {
                principles[principle].issues++;
            }
        }
    });

    return principles;
}

// Update principles summary counts
function updatePrinciplesCounts(perceivable, operable, understandable, robust) {
    document.getElementById('perceivableCount').textContent =
        perceivable === 0 ? '0 issues' : `${perceivable} issue${perceivable !== 1 ? 's' : ''}`;
    document.getElementById('operableCount').textContent =
        operable === 0 ? '0 issues' : `${operable} issue${operable !== 1 ? 's' : ''}`;
    document.getElementById('understandableCount').textContent =
        understandable === 0 ? '0 issues' : `${understandable} issue${understandable !== 1 ? 's' : ''}`;
    document.getElementById('robustCount').textContent =
        robust === 0 ? '0 issues' : `${robust} issue${robust !== 1 ? 's' : ''}`;
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
        findingEl.className = `finding ${finding.severity}`;

        // Sheep status icon - white sheep good, black sheep bad!
        const statusIcon = finding.severity === 'pass'
            ? '<span class="sheep-icon sheep-white">🐑</span>'
            : finding.severity === 'warning'
            ? '<span class="sheep-icon sheep-gray">🐑</span>'
            : '<span class="sheep-icon sheep-black">🐑</span>';

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

        // Build WCAG documentation link
        const wcagDocUrl = getWCAGDocumentationUrl(finding.wcag_reference);
        const docLinkHtml = `
            <div class="finding-links">
                <a href="${wcagDocUrl}" target="_blank" rel="noopener noreferrer" class="doc-link">
                    📖 WCAG ${escapeHtml(finding.wcag_reference)} Documentation
                </a>
            </div>
        `;

        findingEl.innerHTML = `
            <div class="finding-header">
                <div>
                    <div class="finding-title">${statusIcon} ${escapeHtml(finding.rule_code)}</div>
                    <div class="finding-meta">
                        <span>Level: ${escapeHtml(finding.wcag_level)}</span>
                        <span>Principle: ${escapeHtml(finding.principle)}</span>
                        <span>WCAG: ${escapeHtml(finding.wcag_reference)}</span>
                    </div>
                </div>
            </div>
            <div class="finding-message">${escapeHtml(finding.message)}</div>
            ${remediationHtml}
            ${elementPreview}
            ${docLinkHtml}
        `;

        findingsContainer.appendChild(findingEl);
    });
}

// Get WCAG documentation URL for a success criterion
function getWCAGDocumentationUrl(wcagReference) {
    // Map WCAG success criteria to their documentation slugs
    const wcagDocs = {
        '1.1.1': 'non-text-content',
        '1.3.1': 'info-and-relationships',
        '1.4.3': 'contrast-minimum',
        '2.4.2': 'page-titled',
        '2.4.4': 'link-purpose-in-context',
        '2.4.6': 'headings-and-labels',
        '3.1.1': 'language-of-page',
        '3.3.2': 'labels-or-instructions',
        '4.1.1': 'parsing',
        '4.1.2': 'name-role-value'
    };

    const slug = wcagDocs[wcagReference];
    if (slug) {
        return `https://www.w3.org/WAI/WCAG21/Understanding/${slug}.html`;
    }

    // Fallback to quick reference
    return `https://www.w3.org/WAI/WCAG21/quickref/?versions=2.1`;
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
    console.log('⌛ Showing loading state');
    scanForm.classList.add('hidden');
    loadingSection.classList.remove('hidden');
}

// Hide loading state
function hideLoading() {
    console.log('✅ Hiding loading state');
    loadingSection.classList.add('hidden');
    scanForm.classList.remove('hidden');
}

// Show error message
function showError(message) {
    console.error('🚨 Error:', message);
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// Hide error message
function hideError() {
    console.log('✅ Clearing error message');
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
