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

const pdfViewerSection = document.getElementById('pdfViewerSection');
const pdfViewerFrame = document.getElementById('pdfViewerFrame');
const pdfViewerTitle = document.getElementById('pdfViewerTitle');
const openPdfNewTabLink = document.getElementById('openPdfNewTabLink');
const closePdfViewerBtn = document.getElementById('closePdfViewerBtn');

const resumesList = document.getElementById('resumesList');
const refreshBtn = document.getElementById('refreshBtn');

const loadingSpinner = document.getElementById('loadingSpinner');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadResumes();
    setupEventListeners();
    setupUserProfileToggle();
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

    // Close PDF viewer
    if (closePdfViewerBtn) {
        closePdfViewerBtn.addEventListener('click', () => {
            hidePdfViewer();
        });
    }
}

// Profile dropdown: open on icon click, show name + logout (no redirect until logout)
function setupUserProfileToggle() {
    const profileToggle = document.getElementById('profileToggle');
    const profileDropdown = document.getElementById('profileDropdown');
    const profileLogout = document.getElementById('profileLogout');

    if (!profileToggle || !profileDropdown) return;

    const openClass = 'open';

    const setDropdownOpen = (open) => {
        if (open) {
            profileDropdown.classList.add(openClass);
            profileDropdown.setAttribute('aria-hidden', 'false');
            profileToggle.setAttribute('aria-expanded', 'true');
        } else {
            profileDropdown.classList.remove(openClass);
            profileDropdown.setAttribute('aria-hidden', 'true');
            profileToggle.setAttribute('aria-expanded', 'false');
        }
    };

    profileToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        setDropdownOpen(!profileDropdown.classList.contains(openClass));
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!profileDropdown.classList.contains(openClass)) return;
        if (!profileDropdown.contains(e.target) && !profileToggle.contains(e.target)) {
            setDropdownOpen(false);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') setDropdownOpen(false);
    });

    // Logout via fetch (no full-page redirect to /logout), then go to signup
    if (profileLogout) {
        profileLogout.addEventListener('click', async () => {
            setDropdownOpen(false);
            try {
                const res = await fetch(`${API_BASE}/logout`, { method: 'GET', credentials: 'include', redirect: 'manual' });
                // Session cleared; navigate to signup (only redirect is to signup after logout)
                window.location.href = '/signup';
            } catch {
                window.location.href = '/signup';
            }
        });
    }
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
    // alert('handleFilter function called!');
    console.log('handleFilter started');
    
    const keywordsText = keywordsInput.value.trim();
    console.log('Keywords text:', keywordsText);

    if (!keywordsText) {
        showStatus(filterStatus, 'Please enter at least one keyword', 'error');
        return;
    }

    // Parse keywords (comma-separated)
    const keywords = keywordsText
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);
    
    console.log('Parsed keywords:', keywords);

    try {
        showLoading(true);
        console.log('Making API call to:', `${API_BASE}/filter`);
        
        const response = await fetch(`${API_BASE}/filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keywords })
        });

        console.log('API response status:', response.status);
        const data = await response.json();
        console.log('API response data:', data);

        if (response.ok) {
            // alert('About to call displayResults');
            displayResults(data);
            // Check if no results found (0 matches)
            if (data.matched_resumes.length === 0) {
                showStatus(filterStatus, `❌ ${data.message}`, 'error');
            } else {
                showStatus(filterStatus, `✅ ${data.message}`, 'success');
            }
        } else {
            alert('API call failed: ' + data.detail);
            showStatus(filterStatus, `❌ Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        alert('Filter failed with error: ' + error.message);
        showStatus(filterStatus, `❌ Filter failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Display Filter Results
function displayResults(data) {
    // alert('displayResults function called! Check console for details.');
    console.log('displayResults called with:', data);
    resultsContainer.innerHTML = '';

    if (data.matched_resumes.length === 0) {
        resultsContainer.innerHTML = '<div class="no-data">No matching resumes found</div>';
    } else {
        data.matched_resumes.forEach((resume, index) => {
            console.log(`Processing resume ${index}:`, resume);
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            const keywordBadges = resume.matched_keywords
                .map(kw => `<span class="keyword-badge">${kw}</span>`)
                .join('');

            const viewUrl = `${API_BASE}/resumes/view/${encodeURIComponent(resume.filename)}`;
            console.log('Generated viewUrl:', viewUrl);

            resultItem.innerHTML = `
                <div class="result-filename">
                    <div class="result-filename-row">
                        <div class="result-filename-left">
                            📄 <span class="result-filename-text">${escapeHtml(resume.filename)}</span>
                            <span class="result-score">Score: ${resume.score}</span>
                        </div>
                        <button type="button" class="btn btn-primary btn-open" data-view-url="${viewUrl}" title="Open Resume" style="background: red !important; color: white !important; padding: 10px 20px !important; font-size: 14px !important; font-weight: bold !important;">
                            🔓 OPEN RESUME
                        </button>
                    </div>
                </div>
                <div class="result-keywords">
                    ${keywordBadges}
                </div>
            `;

            console.log('Generated HTML for result item:', resultItem.innerHTML);

            const openBtn = resultItem.querySelector('.btn-open');
            console.log('Found open button:', !!openBtn);
            if (openBtn) {
                openBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Open button clicked for:', resume.filename);
                    // Compulsory: always open in the embedded viewer (do not navigate away).
                    showPdfViewer(resume.filename, { required: true });
                });
            }

            resultsContainer.appendChild(resultItem);
            console.log(`Added result item ${index} to container`);
        });
    }

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    console.log('displayResults completed');
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

            const viewUrl = `${API_BASE}/resumes/view/${encodeURIComponent(filename)}`;

            resumeItem.innerHTML = `
                <span class="resume-name">📄 <a href="${viewUrl}" class="resume-link" data-filename="${escapeHtml(filename)}">${escapeHtml(filename)}</a></span>
                <button class="btn btn-delete" type="button">Delete</button>
            `;

            const deleteBtn = resumeItem.querySelector('.btn-delete');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => deleteResume(filename));
            }

            const link = resumeItem.querySelector('.resume-link');
            if (link) {
                link.addEventListener('click', (e) => {
                    const handled = showPdfViewer(filename);
                    if (handled) e.preventDefault();
                });
            }

            resumesList.appendChild(resumeItem);
        });
    }
}

function showPdfViewer(filename, { required = false } = {}) {
    const url = `${API_BASE}/resumes/view/${encodeURIComponent(filename)}`;
    console.log('Attempting to show PDF viewer for:', filename, 'URL:', url);

    if (!pdfViewerSection || !pdfViewerFrame || !pdfViewerTitle || !openPdfNewTabLink) {
        console.error('PDF viewer elements not found:', {
            pdfViewerSection: !!pdfViewerSection,
            pdfViewerFrame: !!pdfViewerFrame,
            pdfViewerTitle: !!pdfViewerTitle,
            openPdfNewTabLink: !!openPdfNewTabLink
        });
        if (required) {
            alert('PDF viewer is not available on this page. Please hard refresh (Ctrl+F5).');
            return false;
        }
        console.warn('PDF viewer elements not found; opening in new tab instead.');
        window.open(url, '_blank');
        return false;
    }

    pdfViewerTitle.textContent = filename;
    openPdfNewTabLink.href = url;
    pdfViewerFrame.src = url;

    pdfViewerSection.style.display = 'block';
    pdfViewerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    console.log('PDF viewer opened successfully for:', filename);
    return true;
}

function hidePdfViewer() {
    if (!pdfViewerSection || !pdfViewerFrame || !pdfViewerTitle || !openPdfNewTabLink) return;
    pdfViewerSection.style.display = 'none';
    pdfViewerTitle.textContent = '';
    openPdfNewTabLink.href = '#';
    pdfViewerFrame.src = 'about:blank';
}

function escapeHtml(str) {
    return String(str)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
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
