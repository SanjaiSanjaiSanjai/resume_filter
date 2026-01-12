// Resume Filtering System - Frontend JavaScript
// Handles all user interactions and API calls

// API Base URL
const API_BASE = window.location.origin;

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileLabel = document.getElementById('fileLabel');
const uploadStatus = document.getElementById('uploadStatus');

const filterForm = document.getElementById('filterForm');
const keywordsInput = document.getElementById('keywordsInput');
const filterStatus = document.getElementById('filterStatus');

const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');

const resumesList = document.getElementById('resumesList');
const refreshBtn = document.getElementById('refreshBtn');

const loadingSpinner = document.getElementById('loadingSpinner');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadResumes();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            fileLabel.textContent = `${files.length} file(s) selected`;
        } else {
            fileLabel.textContent = 'Choose Files';
        }
    });

    // Upload form submit
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleUpload();
    });

    // Filter form submit
    filterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleFilter();
    });

    // Refresh button
    refreshBtn.addEventListener('click', () => {
        loadResumes();
    });
}

// Handle Resume Upload
async function handleUpload() {
    const files = fileInput.files;

    if (files.length === 0) {
        showStatus(uploadStatus, 'Please select at least one file', 'error');
        return;
    }

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(uploadStatus, `✅ ${data.message} (${data.count} files)`, 'success');
            uploadForm.reset();
            fileLabel.textContent = 'Choose Files';
            loadResumes(); // Refresh the list
        } else {
            showStatus(uploadStatus, `❌ Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(uploadStatus, `❌ Upload failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Handle Resume Filter
async function handleFilter() {
    const keywordsText = keywordsInput.value.trim();

    if (!keywordsText) {
        showStatus(filterStatus, 'Please enter at least one keyword', 'error');
        return;
    }

    // Parse keywords (comma-separated)
    const keywords = keywordsText
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keywords })
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
            // Check if no results found (0 matches)
            if (data.matched_resumes.length === 0) {
                showStatus(filterStatus, `❌ ${data.message}`, 'error');
            } else {
                showStatus(filterStatus, `✅ ${data.message}`, 'success');
            }
        } else {
            showStatus(filterStatus, `❌ Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showStatus(filterStatus, `❌ Filter failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Display Filter Results
function displayResults(data) {
    resultsContainer.innerHTML = '';

    if (data.matched_resumes.length === 0) {
        resultsContainer.innerHTML = '<div class="no-data">No matching resumes found</div>';
    } else {
        data.matched_resumes.forEach(resume => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            const keywordBadges = resume.matched_keywords
                .map(kw => `<span class="keyword-badge">${kw}</span>`)
                .join('');

            resultItem.innerHTML = `
                <div class="result-filename">
                    📄 ${resume.filename}
                    <span class="result-score">Score: ${resume.score}</span>
                </div>
                <div class="result-keywords">
                    ${keywordBadges}
                </div>
            `;

            resultsContainer.appendChild(resultItem);
        });
    }

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Load All Resumes
async function loadResumes() {
    try {
        const response = await fetch(`${API_BASE}/resumes`);
        const data = await response.json();

        displayResumesList(data.resumes);
    } catch (error) {
        console.error('Failed to load resumes:', error);
        resumesList.innerHTML = '<div class="no-data">Failed to load resumes</div>';
    }
}

// Display Resumes List
function displayResumesList(resumes) {
    resumesList.innerHTML = '';

    if (resumes.length === 0) {
        resumesList.innerHTML = '<div class="no-data" style="grid-column: 1/-1;">No resumes uploaded yet</div>';
    } else {
        resumes.forEach(filename => {
            const resumeItem = document.createElement('div');
            resumeItem.className = 'resume-item';

            resumeItem.innerHTML = `
                <span class="resume-name">📄 ${filename}</span>
                <button class="btn btn-delete" onclick="deleteResume('${filename}')">Delete</button>
            `;

            resumesList.appendChild(resumeItem);
        });
    }
}

// Delete Resume
async function deleteResume(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/resumes/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            loadResumes(); // Refresh the list
            // Also clear results if showing
            if (resultsSection.style.display !== 'none') {
                resultsSection.style.display = 'none';
            }
        } else {
            alert(`Failed to delete: ${data.detail}`);
        }
    } catch (error) {
        alert(`Delete failed: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Show Status Message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
    element.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Show/Hide Loading Spinner
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}
