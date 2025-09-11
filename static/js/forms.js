// Form JavaScript for Quote Generator

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initializeFormValidation();
    initializeCharacterCounters();
    initializeFormSubmission();
    initializeFormProgress();
    initializeFormMessages();
});

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showFormErrors(form);
            } else {
                showFormLoading(form);
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

// Field Validation
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = `${getFieldLabel(field)} is required.`;
    }

    // Text length validation
    if (fieldName === 'text' && value && value.length < 10) {
        isValid = false;
        errorMessage = 'Quote text must be at least 10 characters long.';
    }

    // Weight validation
    if (fieldName === 'weight' && value) {
        const weight = parseInt(value);
        if (isNaN(weight) || weight < 1 || weight > 100) {
            isValid = false;
            errorMessage = 'Weight must be a number between 1 and 100.';
        }
    }

    // Source validation
    if (fieldName === 'source' && value && value.length < 2) {
        isValid = false;
        errorMessage = 'Source must be at least 2 characters long.';
    }

    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        clearFieldError(field);
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, errorMessage);
    }

    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;

    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    field.classList.remove('is-invalid');
}

// Get field label
function getFieldLabel(field) {
    const label = field.parentNode.querySelector('label');
    return label ? label.textContent.replace('*', '').trim() : field.name;
}

// Show form errors
function showFormErrors(form) {
    const invalidFields = form.querySelectorAll('.is-invalid');
    if (invalidFields.length > 0) {
        invalidFields[0].focus();
        showFormMessage('Please correct the errors below.', 'danger');
    }
}

// Character Counters
function initializeCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[data-max-length]');

    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        if (maxLength) {
            createCharacterCounter(textarea, maxLength);
        }
    });
}

// Create character counter
function createCharacterCounter(field, maxLength) {
    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.textContent = `0 / ${maxLength}`;

    field.parentNode.appendChild(counter);

    field.addEventListener('input', function() {
        const currentLength = this.value.length;
        counter.textContent = `${currentLength} / ${maxLength}`;

        // Update counter appearance
        counter.classList.remove('warning', 'danger');
        if (currentLength > maxLength * 0.9) {
            counter.classList.add('warning');
        }
        if (currentLength > maxLength) {
            counter.classList.add('danger');
        }
    });
}

// Form Submission
function initializeFormSubmission() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                showButtonLoading(submitButton);
            }
        });
    });
}

// Show button loading
function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.classList.add('loading');
    button.disabled = true;

    // Re-enable after 5 seconds as fallback
    setTimeout(() => {
        button.classList.remove('loading');
        button.disabled = false;
        button.innerHTML = originalText;
    }, 5000);
}

// Form Progress
function initializeFormProgress() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const progressBar = form.querySelector('.form-progress-bar');
        if (progressBar) {
            updateFormProgress(form, progressBar);
        }
    });
}

// Update form progress
function updateFormProgress(form, progressBar) {
    const requiredFields = form.querySelectorAll('input[required], textarea[required]');
    const filledFields = Array.from(requiredFields).filter(field => field.value.trim() !== '');

    const progress = (filledFields.length / requiredFields.length) * 100;
    progressBar.style.width = `${progress}%`;
}

// Form Messages
function initializeFormMessages() {
    // Auto-hide success messages after 5 seconds
    const successMessages = document.querySelectorAll('.alert-success');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// Show form message
function showFormMessage(message, type = 'info') {
    const formContainer = document.querySelector('.form-container');
    if (!formContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;

    const messagesContainer = formContainer.querySelector('.form-messages') ||
                            createMessagesContainer(formContainer);

    messagesContainer.appendChild(messageDiv);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

// Create messages container
function createMessagesContainer(container) {
    const messagesDiv = document.createElement('div');
    messagesDiv.className = 'form-messages';
    container.insertBefore(messagesDiv, container.firstChild);
    return messagesDiv;
}

// Form Auto-save (for edit forms)
function initializeAutoSave() {
    const editForms = document.querySelectorAll('form[data-auto-save]');

    editForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        let saveTimeout;

        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    saveFormDraft(form);
                }, 2000);
            });
        });
    });
}

// Save form draft
function saveFormDraft(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }

    localStorage.setItem('quote_form_draft', JSON.stringify(data));
    showFormMessage('Draft saved automatically', 'info');
}

// Load form draft
function loadFormDraft(form) {
    const draft = localStorage.getItem('quote_form_draft');
    if (draft) {
        try {
            const data = JSON.parse(draft);
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
        } catch (e) {
            console.error('Error loading form draft:', e);
        }
    }
}

// Clear form draft
function clearFormDraft() {
    localStorage.removeItem('quote_form_draft');
}

// Form Reset
function resetForm(form) {
    form.reset();
    form.classList.remove('was-validated');

    // Clear validation states
    const fields = form.querySelectorAll('.form-control');
    fields.forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });

    // Clear error messages
    const errorMessages = form.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(message => message.remove());

    // Clear form messages
    const messagesContainer = form.querySelector('.form-messages');
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
    }
}

// Form Enhancement
function enhanceForm(form) {
    // Add floating labels
    const inputs = form.querySelectorAll('.form-control');
    inputs.forEach(input => {
        if (input.value) {
            input.classList.add('has-value');
        }

        input.addEventListener('focus', function() {
            this.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.classList.remove('focused');
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
}

// Initialize form enhancements
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(enhanceForm);
});

// Export functions for external use
window.QuoteForm = {
    showMessage: showFormMessage,
    resetForm: resetForm,
    validateField: validateField,
    clearFormDraft: clearFormDraft
};
