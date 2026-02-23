// Main JavaScript for Sports Summarizer

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Form submission handling
    $('form').on('submit', function() {
        showLoading();
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
    
    // Real-time word count for textareas
    $('textarea').on('input', function() {
        const wordCount = $(this).val().split(/\s+/).filter(word => word.length > 0).length;
        $(this).next('.textarea-counter').find('.word-count').text(wordCount);
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            const hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top - 70
            }, 800);
        }
    });
});

// Show loading spinner
function showLoading() {
    $('body').append(`
        <div class="spinner-container" id="loadingSpinner">
            <div class="spinner"></div>
            <p class="mt-3">Processing your request...</p>
        </div>
    `);
    $('#loadingSpinner').fadeIn();
}

// Hide loading spinner
function hideLoading() {
    $('#loadingSpinner').fadeOut(function() {
        $(this).remove();
    });
}

// API call for quick summarization
function quickSummarize(text, callback) {
    $.ajax({
        url: '/api/summarize-text',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ text: text }),
        success: function(response) {
            if (callback) callback(response);
        },
        error: function(xhr) {
            console.error('Summarization failed:', xhr.responseText);
            if (callback) callback(null);
        }
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showToast('Copied to clipboard!', 'success');
        })
        .catch(err => {
            console.error('Failed to copy:', err);
            showToast('Failed to copy', 'error');
        });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    const toastInstance = new bootstrap.Toast(toast[0]);
    toastInstance.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// File size formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Debounce function for search inputs
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

// Theme switcher (optional)
function toggleTheme() {
    const body = $('body');
    const currentTheme = body.data('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    body.data('theme', newTheme);
    body.attr('data-bs-theme', newTheme);
    
    localStorage.setItem('theme', newTheme);
    showToast(`Switched to ${newTheme} theme`);
}

// Check for saved theme preference
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    $('body').attr('data-bs-theme', savedTheme);
    $('body').data('theme', savedTheme);
}

// Initialize on page load
initTheme();