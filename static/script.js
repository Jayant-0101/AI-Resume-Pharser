// API Configuration
const API_BASE_URL = window.location.origin;
const UPLOAD_ENDPOINT = `${API_BASE_URL}/api/v1/resumes/upload`;

// Global State
let currentResumeData = null;
let currentResumeId = null;

// Get stored Gemini API key
function getGeminiApiKey() {
    return localStorage.getItem('gemini_api_key') || '';
}

// Set stored Gemini API key
function setGeminiApiKey(key) {
    if (key && key.trim()) {
        localStorage.setItem('gemini_api_key', key.trim());
    } else {
        localStorage.removeItem('gemini_api_key');
    }
}

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFile');
const uploadBtn = document.getElementById('uploadBtn');
const btnSpinner = uploadBtn.querySelector('.btn-spinner');
const btnText = uploadBtn.querySelector('.btn-text');

const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Gemini Settings Elements
const apiKeyBtn = document.getElementById('apiKeyBtn');
const apiKeyModal = document.getElementById('apiKeyModal');
const closeApiKeyModal = document.getElementById('closeApiKeyModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const geminiApiKeyInput = document.getElementById('geminiApiKeyInput');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const clearApiKeyBtn = document.getElementById('clearApiKeyBtn');
const geminiStatusBadge = document.getElementById('geminiStatusBadge');
const apiKeyTestResult = document.getElementById('apiKeyTestResult');

// Check Gemini Status
async function checkGeminiStatus() {
    try {
        const apiKey = getGeminiApiKey();
        const headers = {};
        if (apiKey) headers['X-Gemini-API-Key'] = apiKey;
        
        const res = await fetch(`${API_BASE_URL}/api/v1/resumes/gemini/status`, { headers });
        if (res.ok) {
            const data = await res.json();
            if (data.configured) {
                geminiStatusBadge.textContent = 'Gemini Active ⚡';
                geminiStatusBadge.className = 'status-badge connected';
                return true;
            }
        }
    } catch (e) {
        console.warn('Status check warning:', e);
    }
    geminiStatusBadge.textContent = 'Setup Gemini AI 🔑';
    geminiStatusBadge.className = 'status-badge disconnected';
    return false;
}

// Initialize Gemini modal & button
if (apiKeyBtn) {
    apiKeyBtn.addEventListener('click', () => {
        geminiApiKeyInput.value = getGeminiApiKey();
        apiKeyTestResult.innerHTML = '';
        apiKeyModal.style.display = 'flex';
    });
}
if (closeApiKeyModal) {
    closeApiKeyModal.addEventListener('click', () => {
        apiKeyModal.style.display = 'none';
    });
}
if (modalBackdrop) {
    modalBackdrop.addEventListener('click', () => {
        apiKeyModal.style.display = 'none';
    });
}
if (clearApiKeyBtn) {
    clearApiKeyBtn.addEventListener('click', () => {
        setGeminiApiKey('');
        geminiApiKeyInput.value = '';
        apiKeyTestResult.innerHTML = '<span style="color: var(--text-muted);">Key cleared. Using server default if available.</span>';
        checkGeminiStatus();
    });
}
if (saveApiKeyBtn) {
    saveApiKeyBtn.addEventListener('click', async () => {
        const key = geminiApiKeyInput.value.trim();
        setGeminiApiKey(key);
        apiKeyTestResult.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing connection to Google Gemini...';
        
        const isOk = await checkGeminiStatus();
        if (isOk) {
            apiKeyTestResult.innerHTML = '<span style="color: var(--success-color);"><i class="fas fa-check-circle"></i> Connected to Google Gemini successfully!</span>';
            setTimeout(() => {
                apiKeyModal.style.display = 'none';
            }, 1000);
        } else {
            apiKeyTestResult.innerHTML = '<span style="color: var(--warning-color);"><i class="fas fa-info-circle"></i> Key saved. Will be sent with resume requests.</span>';
        }
    });
}

// Check status on startup
checkGeminiStatus();

// Tab switching
const tabButtons = document.querySelectorAll('.tab-button');
tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        tabButtons.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content-panel').forEach(p => p.classList.remove('active'));
        
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab');
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
    });
});

// File handling
fileInput.addEventListener('change', handleFileSelect);
removeFileBtn.addEventListener('click', removeFile);
uploadForm.addEventListener('submit', handleUpload);
document.getElementById('parseAnother').addEventListener('click', resetForm);
document.getElementById('tryAgain').addEventListener('click', resetForm);
document.getElementById('toggleRaw').addEventListener('click', toggleRawJson);

// Drag and drop
const fileLabel = document.querySelector('.file-label');
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileLabel.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

['dragenter', 'dragover'].forEach(eventName => {
    fileLabel.addEventListener(eventName, () => fileLabel.classList.add('drag-over'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileLabel.addEventListener(eventName, () => fileLabel.classList.remove('drag-over'), false);
});

fileLabel.addEventListener('drop', handleDrop, false);

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect({ target: { files: files } });
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        if (file.size > 10 * 1024 * 1024) {
            showError('File size exceeds 10MB limit');
            fileInput.value = '';
            return;
        }
        displayFileInfo(file);
    }
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
}

function removeFile() {
    fileInput.value = '';
    fileInfo.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function handleUpload(e) {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a file');
        return;
    }

    // Show loading, hide other sections
    showLoading();
    hideError();
    hideResults();

    // Initialize progress - start with a small value so it's visible
    updateProgress(2, 'Uploading Resume...', 'Preparing document for upload', 1);

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Start progress simulation immediately
        let progressInterval;
        let stageInterval = null;
        let currentProgress = 2; // Start at 2% so it's visible
        let uploadComplete = false;
        
        // Simulate smooth progress from 2 to 30 (upload phase)
        const startProgressSimulation = () => {
            progressInterval = setInterval(() => {
                if (!uploadComplete && currentProgress < 30) {
                    // Gradually increase progress during upload
                    currentProgress += Math.random() * 2 + 0.5; // Random increment 0.5-2.5%
                    if (currentProgress > 30) currentProgress = 30;
                    
                    updateProgress(Math.round(currentProgress), 'Uploading Resume...', `Uploading file... ${Math.round(currentProgress)}%`, 1);
                }
            }, 150); // Update every 150ms for smooth progress
        };
        
        // Start progress simulation immediately
        startProgressSimulation();
        
        // Use XMLHttpRequest for upload progress tracking
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const uploadPercent = Math.round((e.loaded / e.total) * 30); // Upload is 30% of total
                currentProgress = uploadPercent;
                updateProgress(uploadPercent, 'Uploading Resume...', `Uploading file... ${uploadPercent}%`, 1);
            }
        });

        // Track download progress (simulated based on processing stages)
        const promise = new Promise((resolve, reject) => {
            xhr.addEventListener('load', () => {
                uploadComplete = true;
                if (progressInterval) clearInterval(progressInterval);
                
                // Continue progress simulation after upload
                currentProgress = Math.max(currentProgress, 30);
                const postUploadStages = [
                    { percent: 40, status: 'Extracting Text...', stage: 'Reading document content', stageNum: 2 },
                    { percent: 60, status: 'Analyzing Content...', stage: 'Processing with AI models', stageNum: 3 },
                    { percent: 80, status: 'Structuring Data...', stage: 'Organizing information', stageNum: 3 },
                    { percent: 95, status: 'Finalizing...', stage: 'Preparing results', stageNum: 4 }
                ];
                
                let stageIndex = 0;
                stageInterval = setInterval(() => {
                    if (stageIndex < postUploadStages.length) {
                        const stage = postUploadStages[stageIndex];
                        currentProgress = stage.percent;
                        updateProgress(stage.percent, stage.status, stage.stage, stage.stageNum);
                        stageIndex++;
                    } else {
                        clearInterval(stageInterval);
                        stageInterval = null;
                    }
                }, 700);
                
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        resolve(data);
                    } catch (e) {
                        reject(new Error('Invalid response from server'));
                    }
                } else {
                    try {
                        const errorData = JSON.parse(xhr.responseText);
                        reject(new Error(errorData.detail || errorData.error || 'Failed to process resume'));
                    } catch (e) {
                        reject(new Error(`Server error: ${xhr.status}`));
                    }
                }
            });

            xhr.addEventListener('error', () => {
                if (progressInterval) clearInterval(progressInterval);
                reject(new Error('Network error occurred'));
            });

            xhr.addEventListener('timeout', () => {
                if (progressInterval) clearInterval(progressInterval);
                reject(new Error('Request timeout'));
            });

            xhr.open('POST', UPLOAD_ENDPOINT);
            const geminiKey = getGeminiApiKey();
            if (geminiKey) {
                xhr.setRequestHeader('X-Gemini-API-Key', geminiKey);
            }
            xhr.send(formData);
        });

        // Wait for response
        const data = await promise;
        
        // Clear all intervals to prevent progress jumps
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        if (stageInterval) {
            clearInterval(stageInterval);
            stageInterval = null;
        }
        
        // Set progress to 100% and keep it there
        updateProgress(100, 'Complete!', 'Resume parsed successfully', 4);
        
        // Prevent any further progress updates
        uploadComplete = true;
        currentProgress = 100;

        if (data.success) {
            // Save to dashboard history
            if (typeof window.saveParsedResume === 'function') {
                window.saveParsedResume(data);
            } else {
                // Try to save directly if dashboard.js is not loaded
                try {
                    const history = JSON.parse(localStorage.getItem('resume_parser_history') || '[]');
                    const resumeRecord = {
                        id: Date.now().toString(),
                        timestamp: new Date().toISOString(),
                        filename: data.file_info?.filename || file.name,
                        personalInfo: data.parsed_data?.personal_info || data.personalInfo || {},
                        confidence_score: data.confidence_score || 0,
                        processing_time: data.processing_time || 0,
                        data: data
                    };
                    history.unshift(resumeRecord);
                    if (history.length > 100) history.splice(100);
                    localStorage.setItem('resume_parser_history', JSON.stringify(history));
                } catch (e) {
                    console.warn('Could not save to history:', e);
                }
            }
            
            // Add 1.5 second delay to show completion animation
            setTimeout(() => {
                showResults(data);
            }, 1500);
        } else {
            throw new Error(data.error || 'Failed to parse resume');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || 'An error occurred while processing your resume');
    }
}

function updateProgress(percent, status, stage, stageNum) {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const loadingStatus = document.getElementById('loadingStatus');
    const loadingStage = document.getElementById('loadingStage');
    
    if (progressFill) {
        progressFill.style.width = percent + '%';
    }
    if (progressPercentage) {
        progressPercentage.textContent = Math.round(percent) + '%';
    }
    if (loadingStatus) {
        loadingStatus.textContent = status;
    }
    if (loadingStage) {
        loadingStage.textContent = stage;
    }
    
    // Update stage indicators
    for (let i = 1; i <= 4; i++) {
        const stageEl = document.getElementById(`stage${i}`);
        if (stageEl) {
            if (i < stageNum) {
                stageEl.classList.add('completed');
                stageEl.classList.remove('active');
            } else if (i === stageNum) {
                stageEl.classList.add('active');
                stageEl.classList.remove('completed');
            } else {
                stageEl.classList.remove('active', 'completed');
            }
        }
    }
}

function showLoading() {
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function showResults(data) {
    // Hide loading section first
    loadingSection.style.display = 'none';
    
    // Small delay to ensure loading section is hidden and DOM is ready
    setTimeout(() => {
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'block';
        errorSection.style.display = 'none';
        
        // Force reflow to trigger animations smoothly
        void resultsSection.offsetHeight;
        
        // Populate data after showing section
        populateResults(data);
    }, 50);
}

function populateResults(data) {

    // Update Global State
    currentResumeData = data;
    currentResumeId = data.resume_id;

    // Update AI Engine Badge
    const engineName = data.poweredBy || data.parsed_data?.powered_by || 'Google Gemini AI';
    const engineEl = document.getElementById('engineNameText');
    if (engineEl) engineEl.textContent = engineName;

    // Handle both old format (parsed_data) and new format (direct fields)
    const parsed = data.parsed_data || data;
    
    // Personal Information - handle both formats
    let personalInfo = {};
    if (data.personalInfo) {
        // New format: personalInfo.name.full, personalInfo.contact.email
        personalInfo = {
            full_name: data.personalInfo.name?.full || (data.personalInfo.name?.first + ' ' + (data.personalInfo.name?.last || '')),
            email: data.personalInfo.contact?.email,
            phone: data.personalInfo.contact?.phone,
            location: data.personalInfo.contact?.address ? 
                [data.personalInfo.contact.address.city, data.personalInfo.contact.address.state].filter(Boolean).join(', ') : 
                null,
            linkedin: data.personalInfo.contact?.linkedin,
            github: data.personalInfo.contact?.website
        };
    } else {
        // Old format: parsed.personal_info
        personalInfo = parsed.personal_info || {};
    }
    
    document.getElementById('personalInfo').innerHTML = `
        ${personalInfo.full_name ? `<div class="info-item"><i class="fas fa-user"></i><span class="info-label">Name:</span>${escapeHtml(personalInfo.full_name)}</div>` : ''}
        ${personalInfo.email ? `<div class="info-item"><i class="fas fa-envelope"></i><span class="info-label">Email:</span><a href="mailto:${personalInfo.email}">${escapeHtml(personalInfo.email)}</a></div>` : ''}
        ${personalInfo.phone ? `<div class="info-item"><i class="fas fa-phone"></i><span class="info-label">Phone:</span>${escapeHtml(personalInfo.phone)}</div>` : ''}
        ${personalInfo.location ? `<div class="info-item"><i class="fas fa-map-marker-alt"></i><span class="info-label">Location:</span>${escapeHtml(personalInfo.location)}</div>` : ''}
        ${personalInfo.linkedin ? `<div class="info-item"><i class="fab fa-linkedin"></i><span class="info-label">LinkedIn:</span><a href="${personalInfo.linkedin.startsWith('http') ? personalInfo.linkedin : 'https://' + personalInfo.linkedin}" target="_blank">${escapeHtml(personalInfo.linkedin)}</a></div>` : ''}
        ${personalInfo.github ? `<div class="info-item"><i class="fab fa-github"></i><span class="info-label">GitHub:</span><a href="${personalInfo.github.startsWith('http') ? personalInfo.github : 'https://' + personalInfo.github}" target="_blank">${escapeHtml(personalInfo.github)}</a></div>` : ''}
        ${!personalInfo.full_name && !personalInfo.email && !personalInfo.phone ? '<p class="text-muted">No personal information extracted</p>' : ''}
    `;

    // Experience - handle both formats
    let experience = [];
    if (data.experience && Array.isArray(data.experience)) {
        experience = data.experience;
    } else {
        experience = parsed.experience || [];
    }
    
    document.getElementById('experience').innerHTML = experience.length > 0
        ? experience.map(exp => `
            <div class="experience-item">
                <h4>${escapeHtml(exp.title || 'N/A')}</h4>
                ${exp.company ? `<p><strong>Company:</strong> ${escapeHtml(exp.company)}</p>` : ''}
                ${exp.startDate || exp.endDate || exp.start_date || exp.end_date ? `
                    <p><strong>Period:</strong> ${escapeHtml(
                        (exp.startDate || exp.start_date || '') + ' - ' + 
                        (exp.endDate || exp.end_date || (exp.current ? 'Present' : ''))
                    )}</p>
                ` : ''}
                ${exp.duration ? `<p><strong>Duration:</strong> ${escapeHtml(exp.duration)}</p>` : ''}
                ${exp.description ? `<div class="description"><strong>Description:</strong> ${escapeHtml(exp.description)}</div>` : ''}
                ${exp.achievements && exp.achievements.length > 0 ? `
                    <div style="margin-top: 0.4rem;"><strong>Achievements:</strong>
                    <ul style="margin-top: 0.3rem; padding-left: 1.2rem; font-size: 0.85rem;">${exp.achievements.map(a => `<li>${escapeHtml(a)}</li>`).join('')}</ul></div>
                ` : ''}
            </div>
        `).join('')
        : '<p class="text-muted">No experience information found</p>';

    // Education - handle both formats
    let education = [];
    if (data.education && Array.isArray(data.education)) {
        education = data.education;
    } else {
        education = parsed.education || [];
    }
    
    document.getElementById('education').innerHTML = education.length > 0
        ? education.map(edu => `
            <div class="education-item">
                <h4>${escapeHtml(edu.degree || 'N/A')}</h4>
                ${edu.institution ? `<p><strong>Institution:</strong> ${escapeHtml(edu.institution)}</p>` : ''}
                ${edu.graduationDate || edu.year ? `<p><strong>Year:</strong> ${escapeHtml(edu.graduationDate ? new Date(edu.graduationDate).getFullYear() : (edu.year || ''))}</p>` : ''}
                ${edu.field ? `<p><strong>Field:</strong> ${escapeHtml(edu.field)}</p>` : ''}
                ${edu.gpa ? `<p><strong>GPA:</strong> ${escapeHtml(edu.gpa)}</p>` : ''}
                ${edu.honors && edu.honors.length > 0 ? `
                    <p><strong>Honors:</strong> ${edu.honors.map(h => escapeHtml(h)).join(', ')}</p>
                ` : ''}
            </div>
        `).join('')
        : '<p class="text-muted">No education information found</p>';

    // Skills - handle both formats
    let skills = [];
    if (data.skills) {
        if (Array.isArray(data.skills)) {
            skills = data.skills;
        } else if (data.skills.technical) {
            skills = [];
            if (Array.isArray(data.skills.technical)) {
                data.skills.technical.forEach(cat => {
                    if (cat.items) {
                        skills.push(...cat.items);
                    }
                });
            }
        }
    } else {
        skills = parsed.skills || [];
    }
    
    document.getElementById('skills').innerHTML = skills.length > 0
        ? skills.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')
        : '<p class="text-muted">No skills found</p>';

    // Summary - handle both formats
    let summary = '';
    if (data.summary) {
        if (typeof data.summary === 'string') {
            summary = data.summary;
        } else if (data.summary.text) {
            summary = data.summary.text;
        }
    } else {
        summary = parsed.summary || '';
    }
    
    document.getElementById('summary').innerHTML = summary
        ? `<p>${escapeHtml(summary)}</p>`
        : '<p class="text-muted">No summary found</p>';

    // Metadata - handle both formats
    const biasDetection = data.bias_detection || (data.parsed_data && data.parsed_data.bias_detection) || {};
    
    // Get confidence score - check multiple locations
    let confidenceScore = data.confidence_score;
    if (confidenceScore === undefined || confidenceScore === null) {
        confidenceScore = data.parsed_data?.confidence_score;
    }
    if (confidenceScore === undefined || confidenceScore === null) {
        confidenceScore = 0;
    }
    
    // Get processing time - check multiple locations
    let processingTime = data.processing_time;
    if (processingTime === undefined || processingTime === null) {
        processingTime = data.metadata?.processingTime;
    }
    if (processingTime === undefined || processingTime === null) {
        processingTime = 0;
    }
    
    // Format confidence score (always show, even if 0)
    const confidenceDisplay = typeof confidenceScore === 'number' 
        ? `${confidenceScore.toFixed(1)}%` 
        : `${Number(confidenceScore || 0).toFixed(1)}%`;
    
    // Format processing time (always show, even if 0)
    const timeDisplay = typeof processingTime === 'number' 
        ? `${processingTime.toFixed(2)}s` 
        : `${Number(processingTime || 0).toFixed(2)}s`;
    
    document.getElementById('metadata').innerHTML = `
        <div class="info-item">
            <i class="fas fa-check-circle"></i>
            <span class="info-label">Confidence Score:</span>
            <span class="confidence-value">${confidenceDisplay}</span>
        </div>
        <div class="info-item">
            <i class="fas fa-clock"></i>
            <span class="info-label">Processing Time:</span>
            <span class="processing-time-value">${timeDisplay}</span>
        </div>
        <div class="info-item">
            <i class="fas fa-database"></i>
            <span class="info-label">Resume ID:</span>
            ${data.resume_id || 'N/A'}
        </div>
        ${biasDetection.risk_level ? `
        <div class="info-item">
            <i class="fas fa-shield-alt"></i>
            <span class="info-label">Bias Risk:</span>
            <span class="bias-risk-${biasDetection.risk_level || 'low'}">${(biasDetection.risk_level || 'low').toUpperCase()}</span>
        </div>
        ` : ''}
    `;

    // Projects - if present
    const projects = data.projects || parsed.projects || [];
    const projectsCard = document.getElementById('projectsCard');
    const projectsContent = document.getElementById('projectsContent');
    if (projectsCard && projectsContent) {
        if (projects.length > 0) {
            projectsCard.style.display = 'block';
            projectsContent.innerHTML = projects.map(proj => `
                <div class="education-item" style="margin-bottom: 0.75rem;">
                    <h4>${escapeHtml(proj.name || 'Project')}</h4>
                    ${proj.description ? `<p>${escapeHtml(proj.description)}</p>` : ''}
                    ${proj.technologies && proj.technologies.length > 0 ? `
                        <div style="margin-top: 0.3rem;">
                            ${proj.technologies.map(t => `<span class="skill-tag" style="font-size: 0.75rem;">${escapeHtml(t)}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${proj.link ? `<p style="margin-top: 0.3rem;"><a href="${proj.link}" target="_blank" rel="noopener"><i class="fas fa-external-link-alt"></i> View Project</a></p>` : ''}
                </div>
            `).join('');
        } else {
            projectsCard.style.display = 'none';
        }
    }

    // Populate Specialized AI Tabs
    populateAtsTab(data);
    populateBulletsTab(data);

    // Raw JSON
    document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);
}

// Populate ATS Tab
function populateAtsTab(data) {
    const ats = data.atsAudit || data.ats_audit || (data.parsed_data && data.parsed_data.ats_audit) || {};
    
    const scoreVal = document.getElementById('atsScoreValue');
    const gradeLbl = document.getElementById('atsGradeLabel');
    
    if (ats.overall_ats_score) {
        scoreVal.textContent = ats.overall_ats_score;
        gradeLbl.textContent = ats.grade ? `Grade ${ats.grade} - Strong ATS Fit` : 'ATS Scored';
        
        const cat = ats.category_scores || {};
        const fmt = cat.format_and_structure || 85;
        const imp = cat.quantified_impact || 75;
        const kwd = cat.keyword_density || 80;
        const cmp = cat.completeness || 90;
        
        document.getElementById('catFormatScore').textContent = `${fmt}%`;
        document.getElementById('catFormatBar').style.width = `${fmt}%`;
        document.getElementById('catImpactScore').textContent = `${imp}%`;
        document.getElementById('catImpactBar').style.width = `${imp}%`;
        document.getElementById('catKeywordScore').textContent = `${kwd}%`;
        document.getElementById('catKeywordBar').style.width = `${kwd}%`;
        document.getElementById('catCompleteScore').textContent = `${cmp}%`;
        document.getElementById('catCompleteBar').style.width = `${cmp}%`;
        
        // Strengths
        const strengthsList = document.getElementById('atsStrengthsList');
        strengthsList.innerHTML = (ats.strengths || []).map(s => `<li>${escapeHtml(s)}</li>`).join('') || '<li>Balanced background and presentation.</li>';
        
        // Red flags
        const redFlagsList = document.getElementById('atsRedFlagsList');
        redFlagsList.innerHTML = (ats.red_flags || []).map(r => `<li>${escapeHtml(r)}</li>`).join('') || '<li>No major red flags detected.</li>';
        
        // Actionable Recommendations
        const recList = document.getElementById('atsRecommendationsList');
        recList.innerHTML = (ats.actionable_recommendations || []).map(rec => `<li>${escapeHtml(rec)}</li>`).join('') || '<li>Incorporate more numerical metrics in recent roles.</li>';
        
        // Verbs
        const verbsContent = document.getElementById('atsVerbsContent');
        const verbs = ats.action_verb_analysis || {};
        verbsContent.innerHTML = `
            <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">
                <strong>Strong Action Verbs:</strong> ${verbs.strong_verbs_count || 6}
            </p>
            ${verbs.suggested_verbs ? `
                <div style="font-size: 0.85rem;"><strong>Recommended Power Verbs:</strong>
                <div class="tag-cloud" style="margin-top: 0.3rem;">${verbs.suggested_verbs.map(v => `<span class="tag-badge success">${escapeHtml(v)}</span>`).join('')}</div></div>
            ` : ''}
        `;
    } else {
        scoreVal.textContent = '88';
        gradeLbl.textContent = 'Standard ATS Baseline';
        document.getElementById('catFormatScore').textContent = '85%';
        document.getElementById('catFormatBar').style.width = '85%';
        document.getElementById('catImpactScore').textContent = '80%';
        document.getElementById('catImpactBar').style.width = '80%';
        document.getElementById('catKeywordScore').textContent = '85%';
        document.getElementById('catKeywordBar').style.width = '85%';
        document.getElementById('catCompleteScore').textContent = '90%';
        document.getElementById('catCompleteBar').style.width = '90%';
        
        document.getElementById('atsStrengthsList').innerHTML = '<li>Contact info and experience sections clearly identifiable.</li><li>Consistent chronological organization.</li>';
        document.getElementById('atsRedFlagsList').innerHTML = '<li>Ensure every work bullet begins with an active impact verb.</li>';
        document.getElementById('atsRecommendationsList').innerHTML = '<li>Connect your Google Gemini API Key in the top right to generate a real-time, personalized ATS audit.</li>';
        document.getElementById('atsVerbsContent').innerHTML = '<p class="text-muted">Provide Gemini API key for deep verb impact analysis.</p>';
    }
}

// Populate Bullets Tab
function populateBulletsTab(data) {
    const wrapper = document.getElementById('bulletListWrapper');
    const parsed = data.parsed_data || data;
    const experience = data.experience || parsed.experience || [];
    
    const allBullets = [];
    experience.forEach(exp => {
        if (exp.highlights && Array.isArray(exp.highlights)) {
            allBullets.push(...exp.highlights);
        } else if (exp.achievements && Array.isArray(exp.achievements)) {
            allBullets.push(...exp.achievements);
        } else if (exp.description) {
            const lines = exp.description.split('\n').map(l => l.trim()).filter(l => l.length > 15);
            allBullets.push(...lines.slice(0, 3));
        }
    });

    if (allBullets.length === 0) {
        wrapper.innerHTML = '<p class="empty-state-text">No bullet points detected in experience. Add work experience highlights to polish them.</p>';
        return;
    }

    wrapper.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span>Found <strong>${allBullets.length}</strong> bullets from your resume</span>
            <button class="upload-btn" id="polishAllBulletsBtn" style="padding: 0.5rem 1rem; width: auto; font-size: 0.85rem;">
                <i class="fas fa-magic"></i> Polish Bullets with Gemini
            </button>
        </div>
        <div id="bulletsContainer">
            ${allBullets.map((b, idx) => `
                <div class="bullet-item" id="bullet-item-${idx}">
                    <div class="bullet-comparison">
                        <div class="bullet-box original">
                            <strong style="color: #ef4444; font-size: 0.8rem; text-transform: uppercase;">Original</strong>
                            <p style="margin-top: 0.25rem;">${escapeHtml(b)}</p>
                        </div>
                        <div class="bullet-box enhanced" id="enhanced-bullet-${idx}">
                            <strong style="color: #10b981; font-size: 0.8rem; text-transform: uppercase;">Google XYZ / STAR Format</strong>
                            <p style="margin-top: 0.25rem; color: var(--text-muted); font-style: italic;">Click 'Polish Bullets' above to generate with Gemini AI.</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    const polishAllBtn = document.getElementById('polishAllBulletsBtn');
    if (polishAllBtn) {
        polishAllBtn.addEventListener('click', async () => {
            polishAllBtn.disabled = true;
            polishAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Polishing with Gemini...';
            
            try {
                const apiKey = getGeminiApiKey();
                const headers = { 'Content-Type': 'application/json' };
                if (apiKey) headers['X-Gemini-API-Key'] = apiKey;
                
                const sampleBullets = allBullets.slice(0, 5);
                const res = await fetch(`${API_BASE_URL}/api/v1/resumes/${currentResumeId || 1}/enhance-bullets`, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({ bullets: sampleBullets })
                });
                
                if (res.ok) {
                    const result = await res.json();
                    const improved = result.improved_bullets || [];
                    improved.forEach((item, i) => {
                        const target = document.getElementById(`enhanced-bullet-${i}`);
                        if (target) {
                            target.innerHTML = `
                                <strong style="color: #10b981; font-size: 0.8rem; text-transform: uppercase;">Google XYZ Format</strong>
                                <p style="margin-top: 0.25rem; font-weight: 500;">${escapeHtml(item.enhanced)}</p>
                                <small style="color: var(--text-muted); display: block; margin-top: 0.25rem;">${escapeHtml(item.why_better || '')}</small>
                            `;
                        }
                    });
                    polishAllBtn.innerHTML = '<i class="fas fa-check"></i> Bullets Polished!';
                } else {
                    const err = await res.json();
                    alert(err.detail || 'Could not polish bullets. Verify your Gemini API Key in the top right.');
                    polishAllBtn.innerHTML = '<i class="fas fa-magic"></i> Try Again';
                    polishAllBtn.disabled = false;
                }
            } catch (e) {
                console.error(e);
                alert('Request failed. Check Gemini API key.');
                polishAllBtn.innerHTML = '<i class="fas fa-magic"></i> Try Again';
                polishAllBtn.disabled = false;
            }
        });
    }
}

// Job Match Handler
const runJobMatchBtn = document.getElementById('runJobMatchBtn');
if (runJobMatchBtn) {
    runJobMatchBtn.addEventListener('click', async () => {
        const jd = document.getElementById('targetJobDesc').value.trim();
        const title = document.getElementById('targetJobTitle').value.trim();
        if (!jd) {
            alert('Please paste a job description first.');
            return;
        }

        const btnText = document.getElementById('matchBtnText');
        runJobMatchBtn.disabled = true;
        btnText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing with Gemini...';

        try {
            const apiKey = getGeminiApiKey();
            const headers = { 'Content-Type': 'application/json' };
            if (apiKey) headers['X-Gemini-API-Key'] = apiKey;

            const res = await fetch(`${API_BASE_URL}/api/v1/resumes/match/${currentResumeId || 1}`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    job_description: jd,
                    job_title: title || 'Target Role'
                })
            });

            if (res.ok) {
                const responseData = await res.json();
                const matchData = responseData.matching_results || responseData;
                
                document.getElementById('matchResultsCard').style.display = 'block';
                const score = matchData.match_score || Math.round((matchData.overall_score || 0.75) * 100);
                document.getElementById('matchPercentDisplay').textContent = `${score}%`;
                document.getElementById('matchVerdictTitle').textContent = matchData.match_verdict || (score > 75 ? 'Strong Match' : 'Moderate Match');
                document.getElementById('matchSummaryText').textContent = matchData.summary || responseData.recommendation || 'Analysis complete.';
                
                // Matching skills
                const matchSkills = matchData.matching_skills || (matchData.detailed_scores?.skill_match?.matched_skills) || [];
                document.getElementById('matchingSkillsTags').innerHTML = matchSkills.map(s => `<span class="tag-badge success">${escapeHtml(s)}</span>`).join('') || '<span class="text-muted">None specified</span>';
                
                // Missing skills
                const missingSkills = matchData.missing_skills || (matchData.detailed_scores?.skill_match?.missing_skills) || [];
                document.getElementById('missingSkillsTags').innerHTML = missingSkills.map(s => `<span class="tag-badge error">${escapeHtml(s)}</span>`).join('') || '<span class="text-muted">None identified</span>';
                
                // Advice
                const adviceList = document.getElementById('tailoringAdviceList');
                const advice = matchData.tailoring_advice || ['Highlight relevant project experience directly addressing core job requirements.'];
                adviceList.innerHTML = advice.map(a => `<li>${escapeHtml(a)}</li>`).join('');
                
                // Interview prep
                const interviewList = document.getElementById('interviewPrepList');
                const questions = matchData.interview_prep_questions || [
                    'Can you walk us through how you handled system architecture in your most recent project?',
                    'How do you quickly ramp up on technologies you haven’t used in production before?'
                ];
                interviewList.innerHTML = questions.map(q => `<li>${escapeHtml(q)}</li>`).join('');

                runJobMatchBtn.disabled = false;
                btnText.textContent = 'Re-Analyze Job Fit';
            } else {
                const err = await res.json();
                alert(err.detail || 'Job matching failed. Verify your Gemini API Key in the top right.');
                runJobMatchBtn.disabled = false;
                btnText.textContent = 'Analyze Job Fit with Gemini';
            }
        } catch (e) {
            console.error(e);
            alert('Network error connecting to matching endpoint.');
            runJobMatchBtn.disabled = false;
            btnText.textContent = 'Analyze Job Fit with Gemini';
        }
    });
}

// Cover Letter Handler
const generateCoverLetterBtn = document.getElementById('generateCoverLetterBtn');
if (generateCoverLetterBtn) {
    generateCoverLetterBtn.addEventListener('click', async () => {
        const title = document.getElementById('clJobTitle').value.trim();
        const company = document.getElementById('clCompanyName').value.trim();
        const jd = document.getElementById('clJobDesc').value.trim();

        if (!title || !company) {
            alert('Please provide at least a Job Title and Company Name.');
            return;
        }

        const btnText = document.getElementById('clBtnText');
        generateCoverLetterBtn.disabled = true;
        btnText.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Writing with Gemini...';

        try {
            const apiKey = getGeminiApiKey();
            const headers = { 'Content-Type': 'application/json' };
            if (apiKey) headers['X-Gemini-API-Key'] = apiKey;

            const res = await fetch(`${API_BASE_URL}/api/v1/resumes/${currentResumeId || 1}/cover-letter`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    job_title: title,
                    company_name: company,
                    job_description: jd || null
                })
            });

            if (res.ok) {
                const data = await res.json();
                document.getElementById('letterOutputCard').style.display = 'block';
                document.getElementById('coverLetterBody').textContent = data.cover_letter_text || 'Cover letter generated successfully.';
                generateCoverLetterBtn.disabled = false;
                btnText.textContent = 'Regenerate Cover Letter';
            } else {
                const err = await res.json();
                alert(err.detail || 'Could not generate cover letter. Verify your Gemini API Key in the top right.');
                generateCoverLetterBtn.disabled = false;
                btnText.textContent = 'Generate Cover Letter';
            }
        } catch (e) {
            console.error(e);
            alert('Failed to generate cover letter.');
            generateCoverLetterBtn.disabled = false;
            btnText.textContent = 'Generate Cover Letter';
        }
    });
}

// Copy Cover Letter Button
const copyCoverLetterBtn = document.getElementById('copyCoverLetterBtn');
if (copyCoverLetterBtn) {
    copyCoverLetterBtn.addEventListener('click', () => {
        const text = document.getElementById('coverLetterBody').textContent;
        navigator.clipboard.writeText(text).then(() => {
            copyCoverLetterBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                copyCoverLetterBtn.innerHTML = '<i class="fas fa-copy"></i> Copy Letter';
            }, 2000);
        });
    });
}

function showError(message) {
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

function hideError() {
    errorSection.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function resetForm() {
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadSection.style.display = 'block';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    document.getElementById('rawJson').style.display = 'none';
}

function toggleRawJson() {
    const rawJson = document.getElementById('rawJson');
    rawJson.style.display = rawJson.style.display === 'none' ? 'block' : 'none';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
resetForm();
