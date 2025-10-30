/**
 * Profile & Settings JavaScript
 * Handles profile customization, settings, and notifications
 */

// State management
let profileState = {
    originalData: {},
    unsavedChanges: false,
    notificationPermission: 'default'
};

// Initialize when document loads
document.addEventListener('DOMContentLoaded', () => {
    initializeProfile();
    setupEventListeners();
    checkNotificationPermission();
    loadUserPreferences();
});

/**
 * Initialize profile page
 */
function initializeProfile() {
    loadProfileData();
    setupFormValidation();
    setupPasswordStrengthIndicator();
    updateProfileStats();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Form submissions
    document.getElementById('account-form').addEventListener('submit', handleAccountUpdate);
    document.getElementById('security-form').addEventListener('submit', handlePasswordChange);
    document.getElementById('preferences-form').addEventListener('submit', handlePreferencesUpdate);
    document.getElementById('notifications-form').addEventListener('submit', handleNotificationSettings);
    
    // Real-time updates
    document.getElementById('username').addEventListener('input', updateProfilePreview);
    document.getElementById('email').addEventListener('input', updateProfilePreview);
    document.getElementById('description').addEventListener('input', updateProfilePreview);
    
    // Currency change
    document.getElementById('currency').addEventListener('change', handleCurrencyChange);
    
    // Unsaved changes warning
    window.addEventListener('beforeunload', handlePageUnload);
}

/**
 * Load profile data
 */
function loadProfileData() {
    // For now, load from localStorage or use default values
    const savedProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
    
    profileState.originalData = {
        username: savedProfile.username || 'User',
        email: savedProfile.email || 'user@example.com',
        description: savedProfile.description || 'UNCC Student',
        phone: savedProfile.phone || '',
        currency: savedProfile.currency || 'USD',
        timezone: savedProfile.timezone || 'EST',
        dateFormat: savedProfile.dateFormat || 'MM/DD/YYYY',
        memberSince: savedProfile.memberSince || 'October 2023'
    };
    
    // Populate forms with data
    populateFormData();
}

/**
 * Populate form fields with data
 */
function populateFormData() {
    const data = profileState.originalData;
    
    document.getElementById('username').value = data.username;
    document.getElementById('email').value = data.email;
    document.getElementById('description').value = data.description;
    document.getElementById('phone').value = data.phone;
    document.getElementById('currency').value = data.currency;
    document.getElementById('timezone').value = data.timezone;
    document.getElementById('date-format').value = data.dateFormat;
    
    // Update profile display
    document.getElementById('profile-username').textContent = data.username;
    document.getElementById('profile-email').textContent = data.email;
    document.getElementById('profile-description').textContent = data.description;
    document.getElementById('member-since').textContent = data.memberSince;
}

/**
 * Update profile preview in real-time
 */
function updateProfilePreview() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const description = document.getElementById('description').value;
    
    document.getElementById('profile-username').textContent = username || 'User';
    document.getElementById('profile-email').textContent = email || 'user@example.com';
    document.getElementById('profile-description').textContent = description || 'UNCC Student';
    
    profileState.unsavedChanges = true;
}

/**
 * Handle account information update
 */
async function handleAccountUpdate(e) {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        description: document.getElementById('description').value,
        phone: document.getElementById('phone').value
    };
    
    try {
        showFormLoading(e.target, true);
        
        // Validate data
        if (!validateAccountData(formData)) {
            throw new Error('Please check your input and try again.');
        }
        
        // Save to localStorage for now
        const savedProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        Object.assign(savedProfile, formData);
        localStorage.setItem('userProfile', JSON.stringify(savedProfile));
        
        // Update original data
        Object.assign(profileState.originalData, formData);
        profileState.unsavedChanges = false;
        
        showAlert('Account information updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error updating account:', error);
        showAlert(error.message, 'danger');
    } finally {
        showFormLoading(e.target, false);
    }
}

/**
 * Handle password change
 */
async function handlePasswordChange(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    try {
        showFormLoading(e.target, true);
        
        // Validate passwords
        if (!validatePasswordChange(currentPassword, newPassword, confirmPassword)) {
            throw new Error('Please check your passwords and try again.');
        }
        
        // Simulate password change
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Clear password fields
        document.getElementById('current-password').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
        
        showAlert('Password updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error changing password:', error);
        showAlert(error.message, 'danger');
    } finally {
        showFormLoading(e.target, false);
    }
}

/**
 * Handle preferences update
 */
async function handlePreferencesUpdate(e) {
    e.preventDefault();
    
    const preferences = {
        currency: document.getElementById('currency').value,
        timezone: document.getElementById('timezone').value,
        dateFormat: document.getElementById('date-format').value
    };
    
    try {
        showFormLoading(e.target, true);
        
        // Save preferences
        const savedProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        Object.assign(savedProfile, preferences);
        localStorage.setItem('userProfile', JSON.stringify(savedProfile));
        
        // Apply currency changes immediately
        if (preferences.currency !== profileState.originalData.currency) {
            await updateCurrencyDisplay(preferences.currency);
        }
        
        Object.assign(profileState.originalData, preferences);
        
        showAlert('Preferences updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error updating preferences:', error);
        showAlert(error.message, 'danger');
    } finally {
        showFormLoading(e.target, false);
    }
}

/**
 * Handle notification settings
 */
async function handleNotificationSettings(e) {
    e.preventDefault();
    
    const notifications = {
        goalAchievement: document.getElementById('goal-achievement').checked,
        goalProgress: document.getElementById('goal-progress').checked,
        goalReminders: document.getElementById('goal-reminders').checked,
        budgetAlerts: document.getElementById('budget-alerts').checked,
        weeklySummary: document.getElementById('weekly-summary').checked,
        loginAlerts: document.getElementById('login-alerts').checked
    };
    
    try {
        showFormLoading(e.target, true);
        
        // Save notification preferences
        localStorage.setItem('notificationSettings', JSON.stringify(notifications));
        
        // Request permission if needed
        if (Object.values(notifications).some(enabled => enabled)) {
            await requestNotificationPermission();
        }
        
        showAlert('Notification settings updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error updating notifications:', error);
        showAlert(error.message, 'danger');
    } finally {
        showFormLoading(e.target, false);
    }
}

/**
 * Check notification permission
 */
function checkNotificationPermission() {
    if ('Notification' in window) {
        profileState.notificationPermission = Notification.permission;
        
        if (Notification.permission === 'denied') {
            showAlert('Browser notifications are blocked. Please enable them in your browser settings.', 'warning');
        }
    } else {
        showAlert('Your browser does not support notifications.', 'warning');
    }
}

/**
 * Request notification permission
 */
async function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        const permission = await Notification.requestPermission();
        profileState.notificationPermission = permission;
        
        if (permission === 'granted') {
            showAlert('Notifications enabled successfully!', 'success');
        } else {
            showAlert('Notifications permission denied.', 'warning');
        }
    }
}

/**
 * Test notifications
 */
function testNotifications() {
    const modal = new bootstrap.Modal(document.getElementById('testNotificationModal'));
    modal.show();
}

/**
 * Show test notification
 */
function showTestNotification(type) {
    if (profileState.notificationPermission !== 'granted') {
        requestNotificationPermission().then(() => {
            if (profileState.notificationPermission === 'granted') {
                displayTestNotification(type);
            }
        });
    } else {
        displayTestNotification(type);
    }
    
    // Close modal
    bootstrap.Modal.getInstance(document.getElementById('testNotificationModal')).hide();
}

/**
 * Display test notification
 */
function displayTestNotification(type) {
    const notifications = {
        goal: {
            title: '🎉 Goal Achieved!',
            body: 'Congratulations! You\'ve reached your Emergency Fund goal of $1,000!',
            icon: '/static/images/goal-icon.png'
        },
        budget: {
            title: '⚠️ Budget Alert',
            body: 'You\'ve spent 80% of your monthly dining budget. Consider tracking your expenses.',
            icon: '/static/images/budget-icon.png'
        },
        reminder: {
            title: '⏰ Goal Reminder',
            body: 'Your vacation savings goal deadline is in 2 weeks. You need $200 more to reach it!',
            icon: '/static/images/reminder-icon.png'
        }
    };
    
    const notification = notifications[type];
    
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(notification.title, {
            body: notification.body,
            icon: notification.icon,
            badge: '/static/images/app-icon.png'
        });
    } else {
        // Fallback to browser alert
        alert(`${notification.title}\n\n${notification.body}`);
    }
}

/**
 * Setup password strength indicator
 */
function setupPasswordStrengthIndicator() {
    const passwordInput = document.getElementById('new-password');
    const strengthIndicator = document.getElementById('password-strength');
    
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const strength = calculatePasswordStrength(password);
        
        strengthIndicator.className = `password-strength ${strength.class}`;
        strengthIndicator.style.width = strength.width;
    });
}

/**
 * Calculate password strength
 */
function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    if (score < 2) return { class: 'weak', width: '25%' };
    if (score < 4) return { class: 'fair', width: '50%' };
    if (score < 6) return { class: 'good', width: '75%' };
    return { class: 'strong', width: '100%' };
}

/**
 * Validate account data
 */
function validateAccountData(data) {
    if (!data.username || data.username.trim().length < 3) {
        showAlert('Username must be at least 3 characters long.', 'danger');
        return false;
    }
    
    if (!data.email || !isValidEmail(data.email)) {
        showAlert('Please enter a valid email address.', 'danger');
        return false;
    }
    
    return true;
}

/**
 * Validate password change
 */
function validatePasswordChange(current, newPass, confirm) {
    if (!current) {
        showAlert('Please enter your current password.', 'danger');
        return false;
    }
    
    if (newPass.length < 8) {
        showAlert('New password must be at least 8 characters long.', 'danger');
        return false;
    }
    
    if (newPass !== confirm) {
        showAlert('Password confirmation does not match.', 'danger');
        return false;
    }
    
    return true;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Handle currency change
 */
function handleCurrencyChange() {
    const currency = document.getElementById('currency').value;
    profileState.unsavedChanges = true;
    
    // Show preview of currency change
    showAlert(`Currency will be changed to ${currency} when you save preferences.`, 'info');
}

/**
 * Update currency display throughout the app
 */
async function updateCurrencyDisplay(currency) {
    // This would update all currency displays in the app
    console.log(`Updating currency display to ${currency}`);
    
    // Dispatch event for other parts of the app to listen to
    window.dispatchEvent(new CustomEvent('currencyChanged', { 
        detail: { currency } 
    }));
}

/**
 * Update profile statistics
 */
function updateProfileStats() {
    // Load stats from localStorage or API
    const goals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
    const transactions = JSON.parse(localStorage.getItem('transactions') || '[]');
    
    document.getElementById('goals-count').textContent = goals.length;
    document.getElementById('transactions-count').textContent = transactions.length;
}

/**
 * Load user preferences
 */
function loadUserPreferences() {
    const notifications = JSON.parse(localStorage.getItem('notificationSettings') || '{}');
    
    // Set notification checkboxes
    Object.entries(notifications).forEach(([key, value]) => {
        const element = document.getElementById(key.replace(/([A-Z])/g, '-$1').toLowerCase());
        if (element) {
            element.checked = value;
        }
    });
}

/**
 * Change avatar
 */
function changeAvatar() {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const avatarCircle = document.querySelector('.avatar-circle');
                avatarCircle.innerHTML = `<img src="${e.target.result}" alt="Profile Picture">`;
                
                // Save to localStorage
                localStorage.setItem('userAvatar', e.target.result);
                profileState.unsavedChanges = true;
            };
            reader.readAsDataURL(file);
        }
    };
    
    input.click();
}

/**
 * Export user data
 */
function exportData() {
    try {
        const data = {
            profile: JSON.parse(localStorage.getItem('userProfile') || '{}'),
            goals: JSON.parse(localStorage.getItem('financialGoals') || '[]'),
            transactions: JSON.parse(localStorage.getItem('transactions') || '[]'),
            notifications: JSON.parse(localStorage.getItem('notificationSettings') || '{}')
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `niner-finance-data-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        showAlert('Data exported successfully!', 'success');
        
    } catch (error) {
        console.error('Error exporting data:', error);
        showAlert('Error exporting data.', 'danger');
    }
}

/**
 * Confirm account deletion
 */
function confirmDeleteAccount() {
    const confirmation = prompt('This action cannot be undone. Type "DELETE" to confirm:');
    
    if (confirmation === 'DELETE') {
        if (confirm('Are you absolutely sure? This will permanently delete your account and all data.')) {
            deleteAccount();
        }
    } else if (confirmation !== null) {
        showAlert('Account deletion cancelled - confirmation text did not match.', 'warning');
    }
}

/**
 * Delete user account
 */
async function deleteAccount() {
    try {
        // Clear all user data
        localStorage.removeItem('userProfile');
        localStorage.removeItem('financialGoals');
        localStorage.removeItem('transactions');
        localStorage.removeItem('notificationSettings');
        localStorage.removeItem('userAvatar');
        
        showAlert('Account deleted successfully. Redirecting...', 'success');
        
        // Redirect after delay
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
        
    } catch (error) {
        console.error('Error deleting account:', error);
        showAlert('Error deleting account.', 'danger');
    }
}

/**
 * Show form loading state
 */
function showFormLoading(form, loading) {
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (loading) {
        submitButton.classList.add('loading');
        submitButton.disabled = true;
    } else {
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of settings panel
    const settingsPanel = document.querySelector('.settings-panel');
    settingsPanel.insertBefore(alert, settingsPanel.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Handle page unload
 */
function handlePageUnload(e) {
    if (profileState.unsavedChanges) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return e.returnValue;
    }
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.settings-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Export functions for global access
window.changeAvatar = changeAvatar;
window.testNotifications = testNotifications;
window.showTestNotification = showTestNotification;
window.exportData = exportData;
window.confirmDeleteAccount = confirmDeleteAccount;