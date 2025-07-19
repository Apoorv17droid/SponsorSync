// SponsorSync - Main JavaScript File
// Provides interactive functionality and UX enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeLoadingStates();
    initializeSearchFilters();
    initializeMatchScoreAnimations();
    initializeMessageSystem();
    
    console.log('SponsorSync initialized successfully');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Auto-hide alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Enhanced form validation with real-time feedback
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Scroll to first invalid field
                const firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                    firstInvalidField.focus();
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation for better UX
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    if (this.checkValidity()) {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    }
                }
            });
        });
    });
}

/**
 * Loading states for buttons and forms
 */
function initializeLoadingStates() {
    const submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
    
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                showLoadingState(this);
            }
        });
    });
}

/**
 * Show loading state on button
 */
function showLoadingState(button) {
    const originalText = button.innerHTML;
    const originalDisabled = button.disabled;
    
    button.disabled = true;
    button.innerHTML = '<span class="loading-spinner me-2"></span>Processing...';
    
    // Reset after 10 seconds as fallback
    setTimeout(function() {
        button.disabled = originalDisabled;
        button.innerHTML = originalText;
    }, 10000);
}

/**
 * Enhanced search functionality with suggestions
 */
function initializeSearchFilters() {
    const searchInputs = document.querySelectorAll('.search-input, input[name="keyword"]');
    
    searchInputs.forEach(function(input) {
        let debounceTimer;
        
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                if (input.value.length > 2) {
                    // Could implement live search suggestions here
                    console.log('Searching for:', input.value);
                }
            }, 300);
        });
    });
    
    // Clear search functionality
    const clearButtons = document.querySelectorAll('.btn-clear-search');
    clearButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form) {
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(function(input) {
                    if (input.type === 'submit') return;
                    input.value = '';
                    input.classList.remove('is-valid', 'is-invalid');
                });
                
                // Optionally submit the form to show all results
                // form.submit();
            }
        });
    });
}

/**
 * Animate match score displays
 */
function initializeMatchScoreAnimations() {
    const matchScores = document.querySelectorAll('.match-score, .badge');
    
    // Intersection Observer for animations when elements come into view
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                animateMatchScore(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.5
    });
    
    matchScores.forEach(function(element) {
        if (element.textContent.includes('%')) {
            observer.observe(element);
        }
    });
    
    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        observer.observe(bar);
    });
}

/**
 * Animate individual match score
 */
function animateMatchScore(element) {
    const text = element.textContent;
    const match = text.match(/(\d+)%/);
    
    if (match) {
        const targetValue = parseInt(match[1]);
        let currentValue = 0;
        const increment = Math.ceil(targetValue / 20);
        const duration = 1000; // 1 second
        const stepTime = duration / (targetValue / increment);
        
        const timer = setInterval(function() {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            
            element.textContent = text.replace(/\d+%/, currentValue + '%');
            
            // Update progress bar width if it's a progress bar
            if (element.classList.contains('progress-bar')) {
                element.style.width = currentValue + '%';
            }
        }, stepTime);
    }
}

/**
 * Message system enhancements
 */
function initializeMessageSystem() {
    // Mark messages as read when clicked
    const messageItems = document.querySelectorAll('.message-item, .border-bottom');
    messageItems.forEach(function(item) {
        const readButton = item.querySelector('a[href*="mark_message_read"]');
        if (readButton) {
            readButton.addEventListener('click', function(e) {
                // Add visual feedback
                item.classList.add('opacity-50');
                const newBadge = item.querySelector('.badge.bg-primary');
                if (newBadge) {
                    newBadge.remove();
                }
            });
        }
    });
    
    // Auto-expand message content
    const messageContents = document.querySelectorAll('.message-content');
    messageContents.forEach(function(content) {
        if (content.textContent.length > 150) {
            const truncated = content.textContent.substring(0, 150) + '...';
            const full = content.textContent;
            
            content.innerHTML = truncated + ' <button type="button" class="btn btn-link btn-sm p-0 text-primary">Read more</button>';
            
            const readMoreBtn = content.querySelector('button');
            let expanded = false;
            
            readMoreBtn.addEventListener('click', function() {
                if (!expanded) {
                    content.innerHTML = full + ' <button type="button" class="btn btn-link btn-sm p-0 text-primary">Show less</button>';
                    expanded = true;
                } else {
                    content.innerHTML = truncated + ' <button type="button" class="btn btn-link btn-sm p-0 text-primary">Read more</button>';
                    expanded = false;
                }
                
                // Re-attach event listener to the new button
                const newBtn = content.querySelector('button');
                newBtn.addEventListener('click', arguments.callee);
            });
        }
    });
}

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    const toast = createToastElement(message, type);
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Create toast element
 */
function createToastElement(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const iconMap = {
        'success': 'fas fa-check-circle text-success',
        'error': 'fas fa-exclamation-circle text-danger',
        'warning': 'fas fa-exclamation-triangle text-warning',
        'info': 'fas fa-info-circle text-info'
    };
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="${iconMap[type] || iconMap['info']} me-2"></i>
            <strong class="me-auto">SponsorSync</strong>
            <small>now</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    return toast;
}

/**
 * Enhanced search with keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="keyword"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Escape to clear focused search input
    if (e.key === 'Escape') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName === 'INPUT' && activeElement.name === 'keyword') {
            activeElement.blur();
            activeElement.value = '';
        }
    }
});

/**
 * Smooth scroll for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Copy to clipboard functionality
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    });
}

/**
 * Dynamic badge count updates
 */
function updateBadgeCount(selector, count) {
    const badges = document.querySelectorAll(selector);
    badges.forEach(function(badge) {
        badge.textContent = count;
        if (count > 0) {
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    });
}

/**
 * Image lazy loading for better performance
 */
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(function(img) {
            imageObserver.observe(img);
        });
    }
}

/**
 * Theme toggle functionality (if needed in future)
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

/**
 * Auto-save form data to prevent data loss
 */
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(function(form) {
        const formId = form.id || 'form_' + Math.random().toString(36).substr(2, 9);
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        const savedData = localStorage.getItem('autosave_' + formId);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                inputs.forEach(function(input) {
                    if (data[input.name] && input.type !== 'password') {
                        input.value = data[input.name];
                    }
                });
            } catch (e) {
                console.warn('Failed to load autosave data:', e);
            }
        }
        
        // Save on input
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const formData = {};
                inputs.forEach(function(inp) {
                    if (inp.name && inp.type !== 'password') {
                        formData[inp.name] = inp.value;
                    }
                });
                localStorage.setItem('autosave_' + formId, JSON.stringify(formData));
            });
        });
        
        // Clear on submit
        form.addEventListener('submit', function() {
            localStorage.removeItem('autosave_' + formId);
        });
    });
}

// Initialize autosave if there are forms that need it
document.addEventListener('DOMContentLoaded', function() {
    initializeAutoSave();
});

// Export functions for global use
window.SponsorSync = {
    showToast,
    copyToClipboard,
    updateBadgeCount,
    toggleTheme
};
