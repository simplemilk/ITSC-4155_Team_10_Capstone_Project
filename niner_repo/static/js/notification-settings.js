/**
 * Notification Settings JavaScript
 * Handles settings form interactions and saving
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupSliderUpdates();
    setupFormSubmission();
    setupResetDefaults();
});

/**
 * Setup slider value updates
 */
function setupSliderUpdates() {
    // Budget warning threshold
    const budgetWarningSlider = document.getElementById('budget_warning_threshold');
    const budgetWarningValue = document.getElementById('budget_warning_value');
    if (budgetWarningSlider && budgetWarningValue) {
        budgetWarningSlider.addEventListener('input', function() {
            budgetWarningValue.textContent = this.value + '%';
        });
    }

    // Overspending threshold
    const overspendingSlider = document.getElementById('overspending_threshold');
    const overspendingValue = document.getElementById('overspending_value');
    if (overspendingSlider && overspendingValue) {
        overspendingSlider.addEventListener('input', function() {
            overspendingValue.textContent = this.value + '%';
        });
    }

    // Unusual spending multiplier
    const unusualSpendingSlider = document.getElementById('unusual_spending_multiplier');
    const unusualSpendingValue = document.getElementById('unusual_spending_value');
    if (unusualSpendingSlider && unusualSpendingValue) {
        unusualSpendingSlider.addEventListener('input', function() {
            unusualSpendingValue.textContent = parseFloat(this.value).toFixed(1) + 'x';
        });
    }

    // Max daily notifications
    const maxDailySlider = document.getElementById('max_daily_notifications');
    const maxDailyValue = document.getElementById('max_daily_value');
    if (maxDailySlider && maxDailyValue) {
        maxDailySlider.addEventListener('input', function() {
            maxDailyValue.textContent = this.value;
        });
    }
}

/**
 * Setup form submission
 */
function setupFormSubmission() {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = new FormData(form);
        const settings = {};

        // Process checkboxes (they only appear in FormData if checked)
        const checkboxes = [
            'enable_overspending',
            'enable_budget_warning',
            'enable_unusual_spending',
            'enable_goal_achieved',
            'enable_subscription_reminder',
            'method_in_app',
            'method_email',
            'method_push',
            'daily_digest'
        ];

        checkboxes.forEach(name => {
            const checkbox = form.querySelector(`[name="${name}"]`);
            if (checkbox && !checkbox.disabled) {
                settings[name] = checkbox.checked ? 1 : 0;
            }
        });

        // Process range inputs
        const ranges = [
            'budget_warning_threshold',
            'overspending_threshold',
            'unusual_spending_multiplier',
            'max_daily_notifications'
        ];

        ranges.forEach(name => {
            const input = form.querySelector(`[name="${name}"]`);
            if (input) {
                settings[name] = name === 'unusual_spending_multiplier' 
                    ? parseFloat(input.value) 
                    : parseInt(input.value);
            }
        });

        // Save settings
        try {
            const response = await fetch('/notifications/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();

            if (data.success) {
                showSaveMessage('Settings saved successfully!', 'success');
            } else {
                showSaveMessage(data.error || 'Failed to save settings', 'error');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            showSaveMessage('Error saving settings', 'error');
        }
    });
}

/**
 * Setup reset to defaults button
 */
function setupResetDefaults() {
    const resetBtn = document.getElementById('resetDefaults');
    if (!resetBtn) return;

    resetBtn.addEventListener('click', function() {
        if (!confirm('Reset all settings to default values?')) return;

        // Default values
        const defaults = {
            enable_overspending: true,
            enable_budget_warning: true,
            enable_unusual_spending: true,
            enable_goal_achieved: true,
            enable_subscription_reminder: true,
            budget_warning_threshold: 90,
            overspending_threshold: 100,
            unusual_spending_multiplier: 2.0,
            method_in_app: true,
            method_email: false,
            method_push: false,
            daily_digest: false,
            max_daily_notifications: 10
        };

        // Apply defaults to form
        applySettingsToForm(defaults);

        // Save to server
        saveSettings(defaults);
    });
}

/**
 * Apply settings to form
 */
function applySettingsToForm(settings) {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    // Apply checkboxes
    Object.keys(settings).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'checkbox') {
                input.checked = settings[key];
            } else if (input.type === 'range') {
                input.value = settings[key];
                // Trigger input event to update display
                input.dispatchEvent(new Event('input'));
            }
        }
    });
}

/**
 * Save settings to server
 */
async function saveSettings(settings) {
    try {
        const response = await fetch('/notifications/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        const data = await response.json();

        if (data.success) {
            showSaveMessage('Settings reset to defaults!', 'success');
        } else {
            showSaveMessage(data.error || 'Failed to reset settings', 'error');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        showSaveMessage('Error resetting settings', 'error');
    }
}

/**
 * Show save message
 */
function showSaveMessage(message, type = 'success') {
    const messageEl = document.getElementById('saveMessage');
    if (!messageEl) return;

    messageEl.textContent = message;
    messageEl.className = `save-message ${type === 'error' ? 'error' : ''}`;
    messageEl.classList.add('show');

    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

/**
 * Validate settings before saving
 */
function validateSettings(settings) {
    const errors = [];

    // Validate thresholds
    if (settings.budget_warning_threshold < 0 || settings.budget_warning_threshold > 100) {
        errors.push('Budget warning threshold must be between 0 and 100');
    }

    if (settings.overspending_threshold < 0 || settings.overspending_threshold > 200) {
        errors.push('Overspending threshold must be between 0 and 200');
    }

    if (settings.unusual_spending_multiplier < 1.0 || settings.unusual_spending_multiplier > 10.0) {
        errors.push('Unusual spending multiplier must be between 1.0 and 10.0');
    }

    if (settings.max_daily_notifications < 1 || settings.max_daily_notifications > 50) {
        errors.push('Max daily notifications must be between 1 and 50');
    }

    // Warning threshold should be less than overspending threshold
    if (settings.budget_warning_threshold >= settings.overspending_threshold) {
        errors.push('Budget warning threshold should be less than overspending threshold');
    }

    return errors;
}
