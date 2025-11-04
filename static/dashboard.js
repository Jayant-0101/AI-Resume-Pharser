// Dashboard JavaScript for managing parsed resume history

// Storage key for localStorage
const STORAGE_KEY = 'resume_parser_history';
const MAX_HISTORY = 100; // Maximum number of resumes to keep

// DOM Elements
const resumesList = document.getElementById('resumesList');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const clearHistoryBtn = document.getElementById('clearHistory');
const resumeModal = document.getElementById('resumeModal');
const closeModal = document.getElementById('closeModal');
const modalBody = document.getElementById('modalBody');
const modalTitle = document.getElementById('modalTitle');

// Stats elements
const totalResumesEl = document.getElementById('totalResumes');
const avgProcessingTimeEl = document.getElementById('avgProcessingTime');
const avgConfidenceEl = document.getElementById('avgConfidence');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadResumes();
    setupEventListeners();
    updateStats();
});

// Event Listeners
function setupEventListeners() {
    searchInput.addEventListener('input', () => loadResumes());
    sortSelect.addEventListener('change', () => loadResumes());
    clearHistoryBtn.addEventListener('click', clearHistory);
    closeModal.addEventListener('click', () => {
        resumeModal.style.display = 'none';
    });
    
    // Close modal on outside click
    resumeModal.addEventListener('click', (e) => {
        if (e.target === resumeModal) {
            resumeModal.style.display = 'none';
        }
    });
    
    // Save resume when parsing is successful (called from main page)
    window.addEventListener('storage', (e) => {
        if (e.key === STORAGE_KEY) {
            loadResumes();
            updateStats();
        }
    });
}

// Save parsed resume to localStorage
function saveResume(resumeData) {
    try {
        const history = getResumeHistory();
        
        // Create resume record
        const resumeRecord = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            filename: resumeData.file_info?.filename || 'unknown',
            personalInfo: resumeData.parsed_data?.personal_info || resumeData.personalInfo || {},
            confidence_score: resumeData.confidence_score || 0,
            processing_time: resumeData.processing_time || 0,
            data: resumeData // Store full data
        };
        
        // Add to beginning of array
        history.unshift(resumeRecord);
        
        // Limit history size
        if (history.length > MAX_HISTORY) {
            history.splice(MAX_HISTORY);
        }
        
        // Save to localStorage
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        
        console.log('Resume saved to history:', resumeRecord.id);
        return resumeRecord;
    } catch (error) {
        console.error('Error saving resume:', error);
        // If localStorage is full, try to remove old entries
        if (error.name === 'QuotaExceededError') {
            const history = getResumeHistory();
            // Keep only last 50 entries
            const trimmed = history.slice(0, 50);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
            console.warn('Storage quota exceeded, trimmed history to 50 entries');
        }
    }
}

// Get resume history from localStorage
function getResumeHistory() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Error reading resume history:', error);
        return [];
    }
}

// Load and display resumes
function loadResumes() {
    const history = getResumeHistory();
    const searchTerm = searchInput.value.toLowerCase();
    const sortBy = sortSelect.value;
    
    // Filter resumes
    let filtered = history.filter(resume => {
        if (!searchTerm) return true;
        
        const name = resume.personalInfo?.full_name || '';
        const email = resume.personalInfo?.email || '';
        const filename = resume.filename || '';
        
        return name.toLowerCase().includes(searchTerm) ||
               email.toLowerCase().includes(searchTerm) ||
               filename.toLowerCase().includes(searchTerm);
    });
    
    // Sort resumes
    filtered = sortResumes(filtered, sortBy);
    
    // Display resumes
    if (filtered.length === 0) {
        resumesList.style.display = 'none';
        emptyState.style.display = 'block';
    } else {
        resumesList.style.display = 'grid';
        emptyState.style.display = 'none';
        resumesList.innerHTML = filtered.map(resume => createResumeCard(resume)).join('');
        
        // Add click handlers
        document.querySelectorAll('.resume-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.resume-card-actions')) {
                    const resumeId = card.dataset.id;
                    showResumeDetails(resumeId);
                }
            });
        });
        
        // Add delete handlers
        document.querySelectorAll('.action-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const resumeId = btn.closest('.resume-card').dataset.id;
                deleteResume(resumeId);
            });
        });
    }
}

// Sort resumes
function sortResumes(resumes, sortBy) {
    const sorted = [...resumes];
    
    switch (sortBy) {
        case 'newest':
            return sorted.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        case 'oldest':
            return sorted.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        case 'confidence':
            return sorted.sort((a, b) => (b.confidence_score || 0) - (a.confidence_score || 0));
        case 'name':
            return sorted.sort((a, b) => {
                const nameA = (a.personalInfo?.full_name || '').toLowerCase();
                const nameB = (b.personalInfo?.full_name || '').toLowerCase();
                return nameA.localeCompare(nameB);
            });
        default:
            return sorted;
    }
}

// Create resume card HTML
function createResumeCard(resume) {
    const name = resume.personalInfo?.full_name || 'Unknown';
    const email = resume.personalInfo?.email || 'No email';
    const confidence = resume.confidence_score || 0;
    const processingTime = resume.processing_time || 0;
    const date = new Date(resume.timestamp).toLocaleDateString();
    const time = new Date(resume.timestamp).toLocaleTimeString();
    
    const confidenceClass = confidence >= 70 ? 'confidence-high' : 
                           confidence >= 40 ? 'confidence-medium' : 'confidence-low';
    
    return `
        <div class="resume-card" data-id="${resume.id}">
            <div class="resume-card-header">
                <div class="resume-card-title">
                    <h3>${escapeHtml(name)}</h3>
                    <div class="filename">
                        <i class="fas fa-file"></i> ${escapeHtml(resume.filename)}
                    </div>
                </div>
                <div class="confidence-badge ${confidenceClass}">
                    ${confidence.toFixed(1)}%
                </div>
            </div>
            <div class="resume-card-meta">
                <div class="meta-item">
                    <i class="fas fa-envelope"></i>
                    <span>${escapeHtml(email)}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-clock"></i>
                    <span>${processingTime.toFixed(2)}s</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-calendar"></i>
                    <span>${date} ${time}</span>
                </div>
            </div>
            <div class="resume-card-footer">
                <div class="resume-card-actions">
                    <button class="action-btn delete" title="Delete">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
                <button class="action-btn" onclick="showResumeDetails('${resume.id}')">
                    <i class="fas fa-eye"></i> View Details
                </button>
            </div>
        </div>
    `;
}

// Show resume details in modal
function showResumeDetails(resumeId) {
    const history = getResumeHistory();
    const resume = history.find(r => r.id === resumeId);
    
    if (!resume) {
        alert('Resume not found');
        return;
    }
    
    modalTitle.textContent = resume.personalInfo?.full_name || 'Resume Details';
    modalBody.innerHTML = renderResumeDetails(resume.data || resume);
    resumeModal.style.display = 'flex';
}

// Render resume details (reuse from main script)
function renderResumeDetails(data) {
    const parsed = data.parsed_data || data;
    const personalInfo = parsed.personal_info || data.personalInfo || {};
    
    let html = `
        <div class="results-grid">
            <!-- Personal Information -->
            <div class="result-card personal-info">
                <div class="card-header">
                    <i class="fas fa-user"></i>
                    <h3>Personal Information</h3>
                </div>
                <div class="card-content">
                    ${personalInfo.full_name ? `<div class="info-item"><i class="fas fa-user"></i><span class="info-label">Name:</span>${escapeHtml(personalInfo.full_name)}</div>` : ''}
                    ${personalInfo.email ? `<div class="info-item"><i class="fas fa-envelope"></i><span class="info-label">Email:</span><a href="mailto:${personalInfo.email}">${escapeHtml(personalInfo.email)}</a></div>` : ''}
                    ${personalInfo.phone ? `<div class="info-item"><i class="fas fa-phone"></i><span class="info-label">Phone:</span>${escapeHtml(personalInfo.phone)}</div>` : ''}
                    ${personalInfo.location ? `<div class="info-item"><i class="fas fa-map-marker-alt"></i><span class="info-label">Location:</span>${escapeHtml(personalInfo.location)}</div>` : ''}
                </div>
            </div>
            
            <!-- Experience -->
            <div class="result-card experience">
                <div class="card-header">
                    <i class="fas fa-briefcase"></i>
                    <h3>Experience</h3>
                </div>
                <div class="card-content">
                    ${renderExperience(parsed.experience || data.experience || [])}
                </div>
            </div>
            
            <!-- Education -->
            <div class="result-card education">
                <div class="card-header">
                    <i class="fas fa-graduation-cap"></i>
                    <h3>Education</h3>
                </div>
                <div class="card-content">
                    ${renderEducation(parsed.education || data.education || [])}
                </div>
            </div>
            
            <!-- Skills -->
            <div class="result-card skills">
                <div class="card-header">
                    <i class="fas fa-tools"></i>
                    <h3>Skills</h3>
                </div>
                <div class="card-content">
                    ${renderSkills(parsed.skills || data.skills || [])}
                </div>
            </div>
        </div>
        
        <!-- Metadata -->
        <div class="result-card metadata">
            <div class="card-header">
                <i class="fas fa-info-circle"></i>
                <h3>Processing Info</h3>
            </div>
            <div class="card-content">
                <div class="info-item">
                    <i class="fas fa-chart-line"></i>
                    <span class="info-label">Confidence:</span>
                    ${(data.confidence_score || 0).toFixed(1)}%
                </div>
                <div class="info-item">
                    <i class="fas fa-clock"></i>
                    <span class="info-label">Processing Time:</span>
                    ${(data.processing_time || 0).toFixed(2)}s
                </div>
            </div>
        </div>
    `;
    
    return html;
}

function renderExperience(experience) {
    if (!experience || experience.length === 0) {
        return '<p class="text-muted">No experience information found</p>';
    }
    return experience.map(exp => `
        <div class="experience-item">
            <h4>${escapeHtml(exp.title || 'N/A')}</h4>
            ${exp.company ? `<p><strong>Company:</strong> ${escapeHtml(exp.company)}</p>` : ''}
            ${exp.start_date || exp.end_date ? `<p><strong>Period:</strong> ${escapeHtml((exp.start_date || '') + ' - ' + (exp.end_date || 'Present'))}</p>` : ''}
        </div>
    `).join('');
}

function renderEducation(education) {
    if (!education || education.length === 0) {
        return '<p class="text-muted">No education information found</p>';
    }
    return education.map(edu => `
        <div class="education-item">
            <h4>${escapeHtml(edu.degree || 'N/A')}</h4>
            ${edu.institution ? `<p><strong>Institution:</strong> ${escapeHtml(edu.institution)}</p>` : ''}
            ${edu.year ? `<p><strong>Year:</strong> ${escapeHtml(edu.year)}</p>` : ''}
        </div>
    `).join('');
}

function renderSkills(skills) {
    if (!skills || skills.length === 0) {
        return '<p class="text-muted">No skills found</p>';
    }
    return skills.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('');
}

// Delete resume
function deleteResume(resumeId) {
    if (!confirm('Are you sure you want to delete this resume?')) {
        return;
    }
    
    const history = getResumeHistory();
    const filtered = history.filter(r => r.id !== resumeId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    
    loadResumes();
    updateStats();
}

// Clear all history
function clearHistory() {
    if (!confirm('Are you sure you want to clear all resume history? This cannot be undone.')) {
        return;
    }
    
    localStorage.removeItem(STORAGE_KEY);
    loadResumes();
    updateStats();
}

// Update statistics
function updateStats() {
    const history = getResumeHistory();
    
    totalResumesEl.textContent = history.length;
    
    if (history.length > 0) {
        const avgTime = history.reduce((sum, r) => sum + (r.processing_time || 0), 0) / history.length;
        const avgConf = history.reduce((sum, r) => sum + (r.confidence_score || 0), 0) / history.length;
        
        avgProcessingTimeEl.textContent = avgTime.toFixed(2) + 's';
        avgConfidenceEl.textContent = avgConf.toFixed(1) + '%';
    } else {
        avgProcessingTimeEl.textContent = '0s';
        avgConfidenceEl.textContent = '0%';
    }
}

// Utility function
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions available globally for onclick handlers
window.showResumeDetails = showResumeDetails;

// Auto-save resume when parsing is successful (called from main page)
window.saveParsedResume = function(resumeData) {
    saveResume(resumeData);
    // Trigger storage event for dashboard page if it's open
    window.dispatchEvent(new Event('storage'));
};

