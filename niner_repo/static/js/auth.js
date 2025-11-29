/**
 * Authentication JavaScript
 * Handles login, register, and password functionality
 */

// Global validation functions
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

function validateUsername(username) {
    // Username must be 3+ characters, alphanumeric and underscores only
    return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
}

function validateEmail(email) {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Toggle password visibility - Enhanced version for multiple fields
function togglePassword(fieldId = 'password') {
    const passwordField = document.getElementById(fieldId);
    let toggleIcon = document.getElementById(fieldId + 'ToggleIcon');
    
    // Fallback to generic icon if specific one doesn't exist
    if (!toggleIcon) {
        toggleIcon = document.getElementById('passwordToggleIcon');
    }
    
    if (passwordField && toggleIcon) {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
            toggleIcon.setAttribute('aria-label', 'Hide password');
        } else {
            passwordField.type = 'password';
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
            toggleIcon.setAttribute('aria-label', 'Show password');
        }
    }
}

// Demo login functionality
function demoLogin() {
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const loginForm = document.getElementById('loginForm');
    
    if (usernameField && passwordField && loginForm) {
        // Fill in demo credentials
        usernameField.value = 'demo';
        passwordField.value = 'demo123';
        
        // Add visual feedback
        showAlert('Demo credentials loaded! Logging in...', 'info');
        
        // Submit the form after a short delay for UX
        setTimeout(() => {
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            showLoadingState(submitBtn, 'Signing In...');
            loginForm.submit();
        }, 1000);
    } else {
        // Fallback: redirect to demo endpoint
        window.location.href = '/auth/demo';
    }
}

// Auto-fill demo credentials (without submitting)
function fillDemoCredentials() {
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    
    if (usernameField && passwordField) {
        usernameField.value = 'demo';
        passwordField.value = 'demo123';
        
        // Add visual feedback
        usernameField.classList.add('is-valid');
        passwordField.classList.add('is-valid');
        
        showAlert('Demo credentials filled. Click "Sign In" to continue.', 'success');
        
        // Focus the submit button
        const submitBtn = document.querySelector('#loginForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.focus();
        }
    }
}

// Demo recovery helper function
function fillDemoRecovery() {
    const identifierField = document.getElementById('identifier');
    if (identifierField) {
        identifierField.value = 'demo';
        identifierField.classList.add('is-valid');
        showAlert('Demo username filled! Click continue to proceed.', 'success');
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert:not(.demo-credentials)');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'danger' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of the form container
    const container = document.querySelector('.auth-card') || document.querySelector('form').parentElement;
    const firstChild = container.firstElementChild;
    container.insertBefore(alert, firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

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

// Update password strength indicator
function updatePasswordStrength(password) {
    const strengthBar = document.querySelector('.password-strength-bar');
    
    if (!strengthBar) return;
    
    const validationResults = validatePassword(password);
    const strength = calculatePasswordStrength(password);
    const percentage = (strength / 4) * 100;
    
    // Update strength bar
    strengthBar.style.width = percentage + '%';
    strengthBar.className = 'password-strength-bar';
    
    if (strength === 1) strengthBar.classList.add('strength-weak');
    else if (strength === 2) strengthBar.classList.add('strength-fair');
    else if (strength === 3) strengthBar.classList.add('strength-good');
    else if (strength === 4) strengthBar.classList.add('strength-strong');
    
    // Update each requirement indicator by ID
    updateRequirement('req-length', validationResults.length);
    updateRequirement('req-upper', validationResults.upper);
    updateRequirement('req-lower', validationResults.lower);
    updateRequirement('req-number', validationResults.number);
}

// Helper function to update individual requirement
function updateRequirement(elementId, isMet) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const icon = element.querySelector('i');
    
    if (isMet) {
        element.classList.add('met');
        icon.className = 'fas fa-check me-2';
    } else {
        element.classList.remove('met');
        icon.className = 'fas fa-times me-2';
    }
}

// Form validation
function validateLoginForm(form) {
    const username = form.username.value.trim();
    const password = form.password.value;
    
    if (!username) {
        showAlert('Please enter your username', 'warning');
        form.username.focus();
        return false;
    }
    
    if (!password) {
        showAlert('Please enter your password', 'warning');
        form.password.focus();
        return false;
    }
    
    return true;
}

function validateRegisterForm(form) {
    const username = form.username.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const confirmPassword = form.confirmPassword ? form.confirmPassword.value : '';
    const agreeTerms = form.agreeTerms ? form.agreeTerms.checked : true;
    
    // Security questions validation
    const securityQuestion1 = form.securityQuestion1 ? form.securityQuestion1.value : '';
    const securityAnswer1 = form.securityAnswer1 ? form.securityAnswer1.value.trim() : '';
    const securityQuestion2 = form.securityQuestion2 ? form.securityQuestion2.value : '';
    const securityAnswer2 = form.securityAnswer2 ? form.securityAnswer2.value.trim() : '';
    
    // Validate username
    if (!validateUsername(username)) {
        showAlert('Username must be at least 3 characters and contain only letters, numbers, and underscores', 'danger');
        form.username.focus();
        return false;
    }
    
    // Validate email
    if (!validateEmail(email)) {
        showAlert('Please enter a valid email address', 'danger');
        form.email.focus();
        return false;
    }
    
    // Validate password
    const passwordRequirements = validatePassword(password);
    if (!Object.values(passwordRequirements).every(Boolean)) {
        showAlert('Password must meet all requirements', 'danger');
        form.password.focus();
        return false;
    }
    
    // Validate password confirmation (if field exists)
    if (confirmPassword !== undefined && password !== confirmPassword) {
        showAlert('Password confirmation does not match', 'danger');
        form.confirmPassword.focus();
        return false;
    }
    
    // Validate security questions (if fields exist)
    if (form.securityQuestion1) {
        if (!securityQuestion1) {
            showAlert('Please select the first security question', 'danger');
            form.securityQuestion1.focus();
            return false;
        }
        
        if (!securityAnswer1 || securityAnswer1.length < 2) {
            showAlert('Please provide an answer to the first security question (at least 2 characters)', 'danger');
            form.securityAnswer1.focus();
            return false;
        }
    }
    
    if (form.securityQuestion2) {
        if (!securityQuestion2) {
            showAlert('Please select the second security question', 'danger');
            form.securityQuestion2.focus();
            return false;
        }
        
        if (!securityAnswer2 || securityAnswer2.length < 2) {
            showAlert('Please provide an answer to the second security question (at least 2 characters)', 'danger');
            form.securityAnswer2.focus();
            return false;
        }
    }
    
    // Validate terms agreement (if checkbox exists)
    if (!agreeTerms) {
        showAlert('Please agree to the Terms of Service and Privacy Policy', 'warning');
        return false;
    }
    
    return true;
}

// Form submission handlers
function handleLoginSubmit(e) {
    const form = e.target;
    
    if (!validateLoginForm(form)) {
        e.preventDefault();
        return false;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    showLoadingState(submitBtn, 'Signing In...');
    
    // Form will submit normally
    return true;
}

function handleRegisterSubmit(e) {
    const form = e.target;
    
    if (!validateRegisterForm(form)) {
        e.preventDefault();
        return false;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    showLoadingState(submitBtn, 'Creating Account...');
    
    // Form will submit normally
    return true;
}

// Update the real-time validation to set error messages
function setupRealTimeValidation() {
    const passwordField = document.getElementById('password');
    
    if (passwordField) {
        // Trigger validation on every keystroke
        passwordField.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
        updatePasswordStrength('');
    }
    
    // Username validation with error messages
    const usernameField = document.getElementById('username');
    const usernameError = document.getElementById('username-error');
    
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            const value = this.value;
            
            if (!value) {
                this.classList.remove('is-valid', 'is-invalid');
            } else if (value.length < 3) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (usernameError) usernameError.textContent = 'Username must be at least 3 characters';
            } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (usernameError) usernameError.textContent = 'Only letters, numbers, and underscores allowed';
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    }
    
    // Email validation with error messages
    const emailField = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    
    if (emailField) {
        emailField.addEventListener('blur', function() {
            const value = this.value.trim();
            
            if (!value) {
                this.classList.remove('is-valid', 'is-invalid');
            } else if (!validateEmail(value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (emailError) emailError.textContent = 'Please enter a valid email address';
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    }
    
    // Security answer validation
    const securityAnswers = document.querySelectorAll('[name*="securityAnswer"]');
    securityAnswers.forEach(field => {
        field.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (!value) {
                this.classList.remove('is-valid', 'is-invalid');
            } else if (value.length < 2) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Demo login shortcut (Ctrl/Cmd + D on login page)
        if ((e.ctrlKey || e.metaKey) && e.key === 'd' && document.getElementById('loginForm')) {
            e.preventDefault();
            fillDemoCredentials();
        }
        
        // Quick submit shortcut (Ctrl/Cmd + Enter)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.click();
                }
            }
        }
    });
}

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Accessibility improvements
function enhanceAccessibility() {
    // Add keyboard navigation for password toggle
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        // Add proper ARIA attributes
        toggle.setAttribute('aria-label', 'Toggle password visibility');
        toggle.setAttribute('type', 'button');
        toggle.setAttribute('tabindex', '0');
    });
    
    // Add proper form labels and ARIA attributes
    document.querySelectorAll('input[required]').forEach(input => {
        input.setAttribute('aria-required', 'true');
    });
    
    // Add live region for form validation messages
    if (!document.getElementById('validation-messages')) {
        const liveRegion = document.createElement('div');
        liveRegion.id = 'validation-messages';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.position = 'absolute';
        liveRegion.style.left = '-10000px';
        liveRegion.style.width = '1px';
        liveRegion.style.height = '1px';
        liveRegion.style.overflow = 'hidden';
        document.body.appendChild(liveRegion);
    }
}

// Initialize everything when the DOM loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth.js loaded successfully');
    
    // Initialize theme
    initTheme();
    
    // Enhance accessibility
    enhanceAccessibility();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup real-time validation
    setupRealTimeValidation();
    
    // Add form submission handlers
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
        console.log('Login form handler attached');
        
        // Add demo button functionality if it exists
        const demoButton = document.querySelector('button[onclick*="demoLogin"]');
        if (demoButton) {
            demoButton.removeAttribute('onclick');
            demoButton.addEventListener('click', demoLogin);
        }
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
        console.log('Register form handler attached');
    }
    
    // Add form validation classes
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.classList.add('needs-validation');
    });
    
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
    
    // Security questions form validation
    const securityQuestionsForm = document.getElementById('securityQuestionsForm');
    if (securityQuestionsForm) {
        securityQuestionsForm.addEventListener('submit', function(e) {
            const answer1 = this.answer1 ? this.answer1.value.trim() : '';
            const answer2 = this.answer2 ? this.answer2.value.trim() : '';
            const newPassword = this.newPassword ? this.newPassword.value : '';
            const confirmPassword = this.confirmPassword ? this.confirmPassword.value : '';
            
            if (answer1 && answer2 && (!answer1 || !answer2)) {
                e.preventDefault();
                showAlert('Please answer both security questions.', 'warning');
                return;
            }
            
            if (newPassword && newPassword.length < 8) {
                e.preventDefault();
                showAlert('Password must be at least 8 characters long.', 'warning');
                return;
            }
            
            if (newPassword && confirmPassword && newPassword !== confirmPassword) {
                e.preventDefault();
                showAlert('Passwords do not match.', 'warning');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            showLoadingState(submitBtn, 'Resetting Password...');
        });
        
        // Real-time password confirmation validation
        const newPasswordField = document.getElementById('newPassword');
        const confirmPasswordField = document.getElementById('confirmPassword');
        
        if (newPasswordField && confirmPasswordField) {
            confirmPasswordField.addEventListener('input', function() {
                if (this.value && this.value === newPasswordField.value) {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                } else if (this.value) {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                }
            });
        }
    }
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
    console.error('JavaScript error in auth.js:', e.error);
    
    // Re-enable any disabled buttons as a fallback
    document.querySelectorAll('button[disabled]').forEach(button => {
        if (button.getAttribute('data-original-text')) {
            hideLoadingState(button);
        }
    });
});

// Export functions for global access (if needed)
if (typeof window !== 'undefined') {
    window.togglePassword = togglePassword;
    window.demoLogin = demoLogin;
    window.fillDemoCredentials = fillDemoCredentials;
    window.fillDemoRecovery = fillDemoRecovery;
    window.showAlert = showAlert;
    window.validateEmail = validateEmail;
    window.validateUsername = validateUsername;
    window.validatePassword = validatePassword;
}