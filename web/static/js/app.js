/**
 * StressSpec Web UI - Main JavaScript
 * 
 * This file contains the main JavaScript functionality for the StressSpec web interface.
 * It handles file uploads, analysis progress, and dynamic interactions.
 * 
 * BEGINNER NOTES:
 * - This file contains all the client-side JavaScript logic
 * - It handles file uploads and form submissions
 * - It manages the analysis progress and results display
 * - It integrates with HTMX for dynamic content updates
 */

// Global variables
let currentAnalysisId = null;
let analysisInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('StressSpec Web UI initialized');
    
    // Initialize file upload handling
    initializeFileUpload();
    
    // Initialize HTMX event listeners
    initializeHTMX();
    
    // Initialize tooltips and other Bootstrap components
    initializeBootstrap();
});

/**
 * Initialize file upload functionality
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    
    if (fileInput && uploadForm) {
        // Handle file selection
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                console.log('File selected:', file.name);
                updateFileInfo(file);
            }
        });
        
        // Handle form submission
        uploadForm.addEventListener('submit', handleFileUpload);
    }
}

/**
 * Update file information display
 */
function updateFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    if (fileInfo) {
        fileInfo.innerHTML = `
            <div class="alert alert-info">
                <strong>Selected file:</strong> ${file.name}<br>
                <strong>Size:</strong> ${formatFileSize(file.size)}<br>
                <strong>Type:</strong> ${file.type || 'Unknown'}
            </div>
        `;
    }
}

/**
 * Handle file upload submission
 */
async function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file to upload', 'warning');
        return;
    }
    
    // Validate file
    if (!validateFile(file)) {
        return;
    }
    
    try {
        // Show upload progress
        showUploadProgress();
        
        // Upload file
        const uploadResult = await uploadFile(file);
        
        if (uploadResult.success) {
            showAlert('File uploaded successfully!', 'success');
            
            // Start analysis
            await startAnalysis(uploadResult.file_id);
        } else {
            showAlert('Upload failed: ' + uploadResult.message, 'danger');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('Upload failed: ' + error.message, 'danger');
    }
}

/**
 * Validate uploaded file
 */
function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['.txt', '.md'];
    const allowedMimeTypes = ['text/plain', 'text/markdown'];
    
    // Check file size
    if (file.size > maxSize) {
        showAlert('File too large. Maximum size is 10MB.', 'danger');
        return false;
    }
    
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const mimeType = file.type;
    
    if (!allowedTypes.includes(fileExtension) && !allowedMimeTypes.includes(mimeType)) {
        showAlert('Invalid file type. Please upload a .txt or .md file.', 'danger');
        return false;
    }
    
    return true;
}

/**
 * Upload file to server
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/upload/', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * Start analysis
 */
async function startAnalysis(fileId) {
    try {
        // Show analysis section
        document.getElementById('analysisSection').style.display = 'block';
        
        // Start analysis
        const response = await fetch('/api/analysis/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: fileId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentAnalysisId = result.analysis_id;
            startAnalysisPolling();
        } else {
            showAlert('Failed to start analysis: ' + result.message, 'danger');
        }
    } catch (error) {
        console.error('Analysis start error:', error);
        showAlert('Failed to start analysis: ' + error.message, 'danger');
    }
}

/**
 * Start polling for analysis status
 */
function startAnalysisPolling() {
    if (analysisInterval) {
        clearInterval(analysisInterval);
    }
    
    analysisInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/analysis/status/${currentAnalysisId}`);
            const status = await response.json();
            
            updateAnalysisProgress(status);
            
            if (status.status === 'completed') {
                clearInterval(analysisInterval);
                showAnalysisResults(status.results);
            } else if (status.status === 'error') {
                clearInterval(analysisInterval);
                showAlert('Analysis failed: ' + status.message, 'danger');
            }
        } catch (error) {
            console.error('Status polling error:', error);
            clearInterval(analysisInterval);
            showAlert('Failed to check analysis status', 'danger');
        }
    }, 2000); // Poll every 2 seconds
}

/**
 * Update analysis progress display
 */
function updateAnalysisProgress(status) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    if (progressBar) {
        progressBar.style.width = status.progress + '%';
        progressBar.setAttribute('aria-valuenow', status.progress);
    }
    
    if (progressText) {
        progressText.textContent = status.message;
    }
}

/**
 * Show analysis results
 */
function showAnalysisResults(results) {
    const resultsDiv = document.getElementById('analysisResults');
    const summaryDiv = document.getElementById('resultsSummary');
    
    if (resultsDiv) {
        resultsDiv.style.display = 'block';
    }
    
    if (summaryDiv && results && results.summary) {
        const summary = results.summary;
        
        summaryDiv.innerHTML = `
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title text-primary">${summary.total_requirements || 0}</h5>
                        <p class="card-text">Requirements</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title text-warning">${summary.total_risks || 0}</h5>
                        <p class="card-text">Risks Found</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title text-danger">${summary.requirements_with_risks || 0}</h5>
                        <p class="card-text">With Risks</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <button class="btn btn-primary btn-sm" onclick="downloadReport()">
                            <i class="bi bi-download"></i>
                            Download Report
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
}

/**
 * Download analysis report
 */
async function downloadReport() {
    if (!currentAnalysisId) {
        showAlert('No analysis results available', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/reports/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_id: currentAnalysisId,
                format: 'html'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Open download URL
            window.open(result.download_url, '_blank');
        } else {
            showAlert('Failed to generate report: ' + result.message, 'danger');
        }
    } catch (error) {
        console.error('Report generation error:', error);
        showAlert('Failed to generate report: ' + error.message, 'danger');
    }
}

/**
 * Show upload progress
 */
function showUploadProgress() {
    const progressDiv = document.getElementById('uploadProgress');
    if (progressDiv) {
        progressDiv.style.display = 'block';
    }
}

/**
 * Initialize HTMX event listeners
 */
function initializeHTMX() {
    // HTMX request events
    document.body.addEventListener('htmx:beforeRequest', function(e) {
        console.log('HTMX request starting:', e.detail);
    });
    
    document.body.addEventListener('htmx:afterRequest', function(e) {
        console.log('HTMX request completed:', e.detail);
    });
    
    document.body.addEventListener('htmx:responseError', function(e) {
        console.error('HTMX request error:', e.detail);
        showAlert('Request failed: ' + e.detail.xhr.statusText, 'danger');
    });
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrap() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertDiv, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to throttle function calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}
