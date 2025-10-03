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
    
    // Initialize cancel analysis button
    initializeCancelButton();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
});

/**
 * Initialize file upload functionality
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const uploadZone = document.getElementById('uploadZone');
    const uploadBtn = document.getElementById('uploadBtn');
    const removeFileBtn = document.getElementById('removeFile');
    
    if (fileInput && uploadForm && uploadZone) {
        // Handle file selection
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                console.log('File selected:', file.name);
                handleFileSelection(file);
            }
        });
        
        // Handle drag and drop
        uploadZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        uploadZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (validateFile(file)) {
                    fileInput.files = files;
                    handleFileSelection(file);
                }
            }
        });
        
        // Handle file removal
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function() {
                clearFileSelection();
            });
        }
        
        // Handle form submission
        uploadForm.addEventListener('submit', handleFileUpload);
    }
}

/**
 * Handle file selection
 */
function handleFileSelection(file) {
    if (validateFile(file)) {
        updateFileInfo(file);
        enableUploadButton();
    }
}

/**
 * Clear file selection
 */
function clearFileSelection() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (fileInput) {
        fileInput.value = '';
    }
    
    if (fileInfo) {
        fileInfo.style.display = 'none';
    }
    
    if (uploadBtn) {
        uploadBtn.disabled = true;
    }
}

/**
 * Enable upload button
 */
function enableUploadButton() {
    const uploadBtn = document.getElementById('uploadBtn');
    if (uploadBtn) {
        uploadBtn.disabled = false;
    }
}

/**
 * Update file information display
 */
function updateFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileDetails = document.getElementById('fileDetails');
    
    if (fileInfo && fileName && fileDetails) {
        fileName.textContent = file.name;
        fileDetails.textContent = `${formatFileSize(file.size)} • ${file.type || 'Unknown type'}`;
        fileInfo.style.display = 'block';
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
                showAnalysisError(status.message);
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
    const progressPercent = document.getElementById('progressPercent');
    const cancelBtn = document.getElementById('cancelAnalysis');
    
    if (progressBar) {
        progressBar.style.width = status.progress + '%';
        progressBar.setAttribute('aria-valuenow', status.progress);
    }
    
    if (progressText) {
        progressText.textContent = status.message;
    }
    
    if (progressPercent) {
        progressPercent.textContent = Math.round(status.progress) + '%';
    }
    
    // Update analysis steps based on progress
    updateAnalysisSteps(status.progress);
    
    // Show cancel button during analysis
    if (cancelBtn && status.status === 'processing') {
        cancelBtn.style.display = 'block';
    }
}

/**
 * Update analysis steps based on progress
 */
function updateAnalysisSteps(progress) {
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    
    // Reset all steps
    [step1, step2, step3].forEach(step => {
        if (step) {
            step.classList.remove('active', 'completed');
        }
    });
    
    // Update steps based on progress
    if (progress < 33) {
        if (step1) step1.classList.add('active');
    } else if (progress < 66) {
        if (step1) step1.classList.add('completed');
        if (step2) step2.classList.add('active');
    } else if (progress < 100) {
        if (step1) step1.classList.add('completed');
        if (step2) step2.classList.add('completed');
        if (step3) step3.classList.add('active');
    } else {
        [step1, step2, step3].forEach(step => {
            if (step) step.classList.add('completed');
        });
    }
}

/**
 * Show analysis results
 */
function showAnalysisResults(results) {
    const resultsDiv = document.getElementById('analysisResults');
    const summaryDiv = document.getElementById('resultsSummary');
    const cancelBtn = document.getElementById('cancelAnalysis');
    
    if (resultsDiv) {
        resultsDiv.style.display = 'block';
    }
    
    if (cancelBtn) {
        cancelBtn.style.display = 'none';
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
 * Show analysis error
 */
function showAnalysisError(message) {
    const errorDiv = document.getElementById('analysisError');
    const errorMessage = document.getElementById('errorMessage');
    const cancelBtn = document.getElementById('cancelAnalysis');
    
    if (errorDiv) {
        errorDiv.style.display = 'block';
    }
    
    if (errorMessage) {
        errorMessage.textContent = message;
    }
    
    if (cancelBtn) {
        cancelBtn.style.display = 'none';
    }
}

/**
 * Cancel analysis
 */
async function cancelAnalysis() {
    if (!currentAnalysisId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/analysis/cancel/${currentAnalysisId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            clearInterval(analysisInterval);
            showAlert('Analysis cancelled', 'info');
            resetAnalysisUI();
        } else {
            showAlert('Failed to cancel analysis', 'warning');
        }
    } catch (error) {
        console.error('Cancel analysis error:', error);
        showAlert('Failed to cancel analysis', 'danger');
    }
}

/**
 * Reset analysis UI
 */
function resetAnalysisUI() {
    const analysisSection = document.getElementById('analysisSection');
    const cancelBtn = document.getElementById('cancelAnalysis');
    const errorDiv = document.getElementById('analysisError');
    
    if (analysisSection) {
        analysisSection.style.display = 'none';
    }
    
    if (cancelBtn) {
        cancelBtn.style.display = 'none';
    }
    
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    
    // Reset progress
    updateAnalysisSteps(0);
    
    currentAnalysisId = null;
    if (analysisInterval) {
        clearInterval(analysisInterval);
        analysisInterval = null;
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
 * Initialize cancel analysis button
 */
function initializeCancelButton() {
    const cancelBtn = document.getElementById('cancelAnalysis');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', cancelAnalysis);
    }
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only trigger shortcuts if not typing in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
            return;
        }
        
        // Ctrl/Cmd + U: Focus file upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            if (fileInput) {
                fileInput.click();
            }
        }
        
        // Ctrl/Cmd + Enter: Submit form if file is selected
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const uploadBtn = document.getElementById('uploadBtn');
            if (uploadBtn && !uploadBtn.disabled) {
                uploadBtn.click();
            }
        }
        
        // Escape: Cancel analysis or clear file selection
        if (e.key === 'Escape') {
            if (currentAnalysisId) {
                cancelAnalysis();
            } else {
                clearFileSelection();
            }
        }
        
        // Ctrl/Cmd + R: Refresh page (standard browser behavior)
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            // Allow default behavior
            return;
        }
        
        // F1: Show help
        if (e.key === 'F1') {
            e.preventDefault();
            showKeyboardShortcutsHelp();
        }
    });
}

/**
 * Show keyboard shortcuts help
 */
function showKeyboardShortcutsHelp() {
    const helpModal = `
        <div class="modal fade" id="shortcutsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-keyboard"></i>
                            Keyboard Shortcuts
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>File Operations</h6>
                                <ul class="list-unstyled">
                                    <li><kbd>Ctrl</kbd> + <kbd>U</kbd> - Upload file</li>
                                    <li><kbd>Ctrl</kbd> + <kbd>Enter</kbd> - Start analysis</li>
                                    <li><kbd>Esc</kbd> - Cancel/clear</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Navigation</h6>
                                <ul class="list-unstyled">
                                    <li><kbd>F1</kbd> - Show this help</li>
                                    <li><kbd>Ctrl</kbd> + <kbd>R</kbd> - Refresh page</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('shortcutsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', helpModal);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
    modal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('shortcutsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
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
