/**
 * Password Reset and Forgot Password JavaScript
 * Handles forgot password and reset password functionality
 */

// Global password validation functions
function validatePassword(password) {
    return {
        length: password.length >= 8,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };
}

function calculatePasswordStrength(password) {
    let strength = 0;
    const requirements = validatePassword(password);
    
    if (requirements.length) strength++;
    if (requirements.upper) strength++;
    if (requirements.lower) strength++;
    if (requirements.number) strength++;
    
    return strength;
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateUsername(username) {
    return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
}

// Password toggle functionality
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const toggleIcon = document.getElementById(fieldId + 'ToggleIcon');
    
    if (passwordField && toggleIcon) {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
    }
}

// Alert functionality
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert:not([data-permanent])');
    existingAlerts.forEach(alert => alert.remove());

    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert alert at the top of the auth card
    const authCard = document.querySelector('.auth-card');
    const firstChild = authCard.firstElementChild;
    authCard.insertBefore(alert, firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Loading state functionality
function showLoadingState(button, text = 'Loading...') {
    if (!button) return;
    
    const originalText = button.innerHTML;
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
    button.disabled = true;
    
    // Store original text to restore later
    button.setAttribute('data-original-text', originalText);
}

function hideLoadingState(button) {
    if (!button) return;
    
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
        button.removeAttribute('data-original-text');
    }
}

// Password strength indicator
function updatePasswordStrengthBar(strength) {
    const bar = document.getElementById('strengthBar');
    if (!bar) return;
    
    const percentage = (strength / 4) * 100;
    bar.style.width = percentage + '%';
    
    // Remove all strength classes
    bar.className = 'password-strength-bar';
    
    if (strength === 1) bar.classList.add('strength-weak');
    else if (strength === 2) bar.classList.add('strength-fair');
    else if (strength === 3) bar.classList.add('strength-good');
    else if (strength === 4) bar.classList.add('strength-strong');
}

// Password requirement indicators
function updateRequirement(id, met) {
    const element = document.getElementById(id);
    if (!element) return;
    
    const icon = element.querySelector('i');
    
    if (met) {
        element.classList.add('met');
        icon.className = 'fas fa-check me-2';
    } else {
        element.classList.remove('met');
        icon.className = 'fas fa-times me-2';
    }
}

function updatePasswordRequirements(password) {
    const requirements = validatePassword(password);
    
    // Update requirement indicators
    updateRequirement('lengthReq', requirements.length);
    updateRequirement('upperReq', requirements.upper);
    updateRequirement('lowerReq', requirements.lower);
    updateRequirement('numberReq', requirements.number);
    
    // Update strength bar
    const strength = calculatePasswordStrength(password);
    updatePasswordStrengthBar(strength);
    
    return Object.values(requirements).every(Boolean);
}

// Forgot Password Page Functions
function initForgotPasswordPage() {
    const form = document.getElementById('forgotPasswordForm');
    const identifierField = document.getElementById('identifier');
    const submitBtn = document.getElementById('submitBtn');

    // Focus on identifier field
    if (identifierField) {
        identifierField.focus();
    }

    // Form validation
    if (identifierField) {
        identifierField.addEventListener('input', validateIdentifier);
        identifierField.addEventListener('blur', validateIdentifier);
    }

    function validateIdentifier() {
        const value = identifierField.value.trim();
        
        if (!value) {
            identifierField.classList.remove('is-valid', 'is-invalid');
            return false;
        }

        // Check if it's email or username
        const isEmail = validateEmail(value);
        const isUsername = validateUsername(value);

        if (isEmail || isUsername) {
            identifierField.classList.remove('is-invalid');
            identifierField.classList.add('is-valid');
            return true;
        } else {
            identifierField.classList.remove('is-valid');
            identifierField.classList.add('is-invalid');
            return false;
        }
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            const isValid = validateIdentifier();

            if (!isValid) {
                e.preventDefault();
                showAlert('Please enter a valid username or email address', 'danger');
                return false;
            }

            // Show loading state
            if (submitBtn) {
                showLoadingState(submitBtn, 'Sending...');
            }

            return true;
        });
    }

    // Check for success parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('sent') === 'true') {
        showResetSuccessModal();
    }
}

// Reset Password Page Functions
function initResetPasswordPage() {
    const form = document.getElementById('resetPasswordForm');
    const newPasswordField = document.getElementById('newPassword');
    const confirmPasswordField = document.getElementById('confirmPassword');
    const submitBtn = document.getElementById('submitBtn');

    // Focus on password field
    if (newPasswordField) {
        newPasswordField.focus();
    }

    // Event listeners
    if (newPasswordField) {
        newPasswordField.addEventListener('input', function() {
            const isValid = updatePasswordRequirements(this.value);
            
            if (this.value && isValid) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else if (this.value) {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
            
            // Also validate confirm password if it has a value
            if (confirmPasswordField && confirmPasswordField.value) {
                validateConfirmPassword();
            }
        });
    }

    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', validateConfirmPassword);
    }

    function validateConfirmPassword() {
        if (!newPasswordField || !confirmPasswordField) return false;
        
        const password = newPasswordField.value;
        const confirmPassword = confirmPasswordField.value;
        
        if (confirmPassword && password === confirmPassword) {
            confirmPasswordField.classList.remove('is-invalid');
            confirmPasswordField.classList.add('is-valid');
            return true;
        } else if (confirmPassword) {
            confirmPasswordField.classList.remove('is-valid');
            confirmPasswordField.classList.add('is-invalid');
        }
        return false;
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            const password = newPasswordField.value;
            const confirmPassword = confirmPasswordField.value;
            
            const passwordRequirements = validatePassword(password);
            const passwordValid = Object.values(passwordRequirements).every(Boolean);
            const passwordsMatch = password === confirmPassword;
            
            if (!passwordValid) {
                e.preventDefault();
                newPasswordField.classList.add('is-invalid');
                showAlert('Password must meet all requirements', 'danger');
                return false;
            }
            
            if (!passwordsMatch) {
                e.preventDefault();
                confirmPasswordField.classList.add('is-invalid');
                showAlert('Passwords do not match', 'danger');
                return false;
            }
            
            // Show loading state
            if (submitBtn) {
                showLoadingState(submitBtn, 'Resetting Password...');
            }
            
            return true;
        });
    }
}

// Modal Functions
function showSecurityQuestions() {
    const identifier = document.getElementById('identifier').value.trim();
    
    if (!identifier) {
        showAlert('Please enter your username or email first', 'warning');
        document.getElementById('identifier').focus();
        return;
    }

    const modal = document.getElementById('securityQuestionsModal');
    if (modal && typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modal).show();
    }
}

function verifySecurityQuestions() {
    const question1 = document.getElementById('question1').value.trim();
    const question2 = document.getElementById('question2').value.trim();
    const question3 = document.getElementById('question3').value.trim();

    if (!question1 || !question2 || !question3) {
        alert('Please answer all security questions');
        return;
    }

    // In a real application, you would verify these against stored answers
    // For demo purposes, we'll simulate a successful verification
    const modal = bootstrap.Modal.getInstance(document.getElementById('securityQuestionsModal'));
    modal.hide();

    showAlert('Security questions verified! Redirecting to password reset...', 'success');
    
    setTimeout(() => {
        // In real app, use actual reset URL with valid token
        window.location.href = window.location.origin + '/auth/reset-password?token=demo-token';
    }, 2000);
}

function contactSupport() {
    const modal = document.getElementById('contactSupportModal');
    if (modal && typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modal).show();
    }
}

function startLiveChat() {
    // In a real application, this would integrate with a live chat service
    alert('Live chat feature coming soon! Please use email or phone support for now.');
}

function showResetSuccessModal() {
    const modal = document.getElementById('resetSuccessModal');
    if (modal && typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modal).show();
    }
}

function resendResetEmail() {
    const identifier = new URLSearchParams(window.location.search).get('identifier');
    
    if (identifier) {
        // Make request to resend email
        fetch(window.location.origin + '/auth/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `identifier=${encodeURIComponent(identifier)}&resend=true`
        })
        .then(response => {
            if (response.ok) {
                showAlert('Reset email sent again!', 'success');
            } else {
                showAlert('Error resending email. Please try again.', 'danger');
            }
        })
        .catch(error => {
            showAlert('Error resending email. Please try again.', 'danger');
        });
    }
}

// Initialize page based on which form is present
document.addEventListener('DOMContentLoaded', function() {
    console.log('Password.js loaded successfully');

    // Determine which page we're on and initialize accordingly
    if (document.getElementById('forgotPasswordForm')) {
        initForgotPasswordPage();
    } else if (document.getElementById('resetPasswordForm')) {
        initResetPasswordPage();
    }

    // Handle potential error messages from Flask
    const errorMessages = document.querySelectorAll('.flash-message');
    errorMessages.forEach(msg => {
        const type = msg.classList.contains('alert-danger') ? 'danger' : 
                    msg.classList.contains('alert-warning') ? 'warning' : 
                    msg.classList.contains('alert-success') ? 'success' : 'info';
        
        // Don't duplicate if it's already an alert
        if (!msg.classList.contains('alert')) {
            showAlert(msg.textContent, type);
            msg.remove();
        }
    });
});

// Handle form errors on page load (from Flask flash messages)
window.addEventListener('load', function() {
    // Check for URL parameters that indicate errors
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const success = urlParams.get('success');
    
    if (error) {
        showAlert(decodeURIComponent(error), 'danger');
    }
    
    if (success) {
        showAlert(decodeURIComponent(success), 'success');
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error in password.js:', e.error);
    
    // Re-enable any disabled buttons as a fallback
    document.querySelectorAll('button[disabled]').forEach(button => {
        if (button.getAttribute('data-original-text')) {
            hideLoadingState(button);
        }
    });
});

// Export functions for global access
if (typeof window !== 'undefined') {
    window.togglePassword = togglePassword;
    window.showAlert = showAlert;
    window.showSecurityQuestions = showSecurityQuestions;
    window.verifySecurityQuestions = verifySecurityQuestions;
    window.contactSupport = contactSupport;
    window.startLiveChat = startLiveChat;
    window.showResetSuccessModal = showResetSuccessModal;
    window.resendResetEmail = resendResetEmail;
}