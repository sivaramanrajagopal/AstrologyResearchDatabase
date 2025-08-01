// Astrological Birth Chart Database - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time form validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        if (isRequired && !value) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
        } else if (value) {
            field.classList.add('is-valid');
            field.classList.remove('is-invalid');
        } else {
            field.classList.remove('is-valid', 'is-invalid');
        }
    }

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = width;
        }, 100);
    });

    // Table row hover effects
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Export functionality
    const exportButtons = document.querySelectorAll('[data-export]');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const format = this.getAttribute('data-export');
            const category = this.getAttribute('data-category') || '';
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
            this.disabled = true;
            
            // Simulate export process
            setTimeout(function() {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        });
    });

    // Search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Category filter enhancement
    const categorySelect = document.querySelector('#category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const selectedCategory = this.value;
            const url = new URL(window.location);
            
            if (selectedCategory) {
                url.searchParams.set('category', selectedCategory);
            } else {
                url.searchParams.delete('category');
            }
            
            window.location.href = url.toString();
        });
    }

    // Auto-save form data to localStorage
    const formsToSave = document.querySelectorAll('form[data-autosave]');
    formsToSave.forEach(function(form) {
        const formId = form.id || 'birthChartForm';
        
        // Load saved data
        const savedData = localStorage.getItem(formId);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(function(key) {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
        }
        
        // Save data on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(formId, JSON.stringify(data));
            });
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(formId);
        });
    });

    // Responsive table enhancement
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(function(table) {
        const wrapper = table.parentElement;
        const scrollIndicator = document.createElement('div');
        scrollIndicator.className = 'scroll-indicator';
        scrollIndicator.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Scroll to see more';
        scrollIndicator.style.cssText = 'text-align: center; color: #6c757d; font-size: 0.875rem; margin-top: 0.5rem;';
        
        if (table.scrollWidth > table.clientWidth) {
            wrapper.appendChild(scrollIndicator);
        }
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N for new chart
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('a[href*="add_birth_chart"]');
            if (addButton) {
                window.location.href = addButton.href;
            }
        }
        
        // Ctrl/Cmd + S for save (if on form page)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    });

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Data visualization helpers
    function createProgressBar(percentage, color = 'primary') {
        return `
            <div class="progress" style="height: 8px;">
                <div class="progress-bar bg-${color}" style="width: ${percentage}%"></div>
            </div>
        `;
    }

    // Export this function for use in templates
    window.createProgressBar = createProgressBar;
});

// Utility functions
window.AstroDB = {
    // Format date for display
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    },
    
    // Format time for display
    formatTime: function(timeString) {
        const [hours, minutes] = timeString.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${minutes} ${ampm}`;
    },
    
    // Calculate age from birth date
    calculateAge: function(birthDate) {
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    },
    
    // Validate birth time format
    validateTime: function(timeString) {
        const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
        return timeRegex.test(timeString);
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            const alert = new bootstrap.Alert(alertDiv);
            alert.close();
        }, 5000);
    }
}; 