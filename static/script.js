// API Configuration
const API_BASE_URL = window.location.origin;
const UPLOAD_ENDPOINT = `${API_BASE_URL}/api/v1/resumes/upload`;

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

    // Raw JSON
    document.getElementById('rawJson').textContent = JSON.stringify(data, null, 2);
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
