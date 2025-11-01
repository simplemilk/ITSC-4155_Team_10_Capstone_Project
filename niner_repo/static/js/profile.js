// Simple Profile JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initProfileForm();
});

function initProfileForm() {
    const form = document.getElementById('profileForm');
    const emailField = document.getElementById('email');
    const currentPasswordField = document.getElementById('currentPassword');
    const newPasswordField = document.getElementById('newPassword');
    const confirmPasswordField = document.getElementById('confirmPassword');

    // Form validation
    if (form) {
        form.addEventListener('submit', function(e) {
            clearErrors();
            
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Real-time validation
    if (emailField) {
        emailField.addEventListener('blur', validateEmail);
    }

    if (newPasswordField) {
        newPasswordField.addEventListener('input', function() {
            validatePasswordMatch();
            validatePasswordLength();
        });
    }

    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', validatePasswordMatch);
    }

    // Clear password fields if user clicks away without entering current password
    if (currentPasswordField) {
        currentPasswordField.addEventListener('blur', function() {
            if (!this.value && (newPasswordField.value || confirmPasswordField.value)) {
                showError('Current password is required to change password');
                this.classList.add('is-invalid');
            }
        });
    }
}

function validateForm() {
    let isValid = true;

    // Validate email
    if (!validateEmail()) {
        isValid = false;
    }

    // Validate password fields if changing password
    const newPassword = document.getElementById('newPassword').value;
    const currentPassword = document.getElementById('currentPassword').value;

    if (newPassword) {
        if (!currentPassword) {
            showError('Current password is required to change password');
            document.getElementById('currentPassword').classList.add('is-invalid');
            isValid = false;
        }

        if (!validatePasswordLength()) {
            isValid = false;
        }

        if (!validatePasswordMatch()) {
            isValid = false;
        }
    }

    return isValid;
}

function validateEmail() {
    const emailField = document.getElementById('email');
    const email = emailField.value.trim();
    
    if (!email) {
        showError('Email is required');
        emailField.classList.add('is-invalid');
        return false;
    }

    if (!email.includes('@') || !email.includes('.')) {
        showError('Please enter a valid email address');
        emailField.classList.add('is-invalid');
        return false;
    }

    emailField.classList.remove('is-invalid');
    return true;
}

function validatePasswordLength() {
    const newPasswordField = document.getElementById('newPassword');
    const password = newPasswordField.value;

    if (password && password.length < 8) {
        showError('New password must be at least 8 characters');
        newPasswordField.classList.add('is-invalid');
        return false;
    }

    newPasswordField.classList.remove('is-invalid');
    return true;
}

function validatePasswordMatch() {
    const newPasswordField = document.getElementById('newPassword');
    const confirmPasswordField = document.getElementById('confirmPassword');
    const newPassword = newPasswordField.value;
    const confirmPassword = confirmPasswordField.value;

    if (newPassword && confirmPassword && newPassword !== confirmPassword) {
        showError('New passwords do not match');
        confirmPasswordField.classList.add('is-invalid');
        return false;
    }

    confirmPasswordField.classList.remove('is-invalid');
    return true;
}

function showError(message) {
    // Remove existing error alerts
    const existingErrors = document.querySelectorAll('.alert-error.js-error');
    existingErrors.forEach(error => error.remove());

    // Create new error alert
    const alert = document.createElement('div');
    alert.className = 'alert alert-error js-error';
    alert.textContent = message;

    // Insert at top of profile card
    const profileCard = document.querySelector('.profile-card');
    const firstChild = profileCard.querySelector('.profile-header').nextElementSibling;
    profileCard.insertBefore(alert, firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function clearErrors() {
    // Remove error styling
    document.querySelectorAll('.form-control.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });

    // Remove JavaScript-generated error messages
    document.querySelectorAll('.alert-error.js-error').forEach(error => {
        error.remove();
    });
}

// Show confirmation when form is submitted successfully
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.textContent = message;

    const profileCard = document.querySelector('.profile-card');
    const firstChild = profileCard.querySelector('.profile-header').nextElementSibling;
    profileCard.insertBefore(alert, firstChild);
}

// Utility function to check if passwords are being changed
function isChangingPassword() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const currentPassword = document.getElementById('currentPassword').value;
    
    return newPassword || confirmPassword || currentPassword;
}

// Clear password fields function
function clearPasswordFields() {
    document.getElementById('currentPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    clearErrors();
}

// Add this to global scope for potential external use
window.clearPasswordFields = clearPasswordFields;