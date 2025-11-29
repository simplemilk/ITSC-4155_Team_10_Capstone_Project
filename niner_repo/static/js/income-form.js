document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('incomeForm'); // Updated ID to match template
    const recurringCheckbox = document.getElementById('is_recurring');
    const recurrenceDiv = document.getElementById('recurrence_div');
    const dateInput = document.getElementById('date');

    // Set today's date as default
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Show/hide recurrence period based on checkbox
    if (recurringCheckbox && recurrenceDiv) {
        recurringCheckbox.addEventListener('change', function() {
            recurrenceDiv.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Validation functions
    const validateAmount = (value) => {
        const amount = parseFloat(value);
        return amount > 0;
    };

    const validateSource = (value) => {
        return value.trim().length > 0 && value.trim().length <= 100;
    };

    const validateDate = (value) => {
        const date = new Date(value);
        const today = new Date();
        today.setHours(23, 59, 59, 999); // Allow today's date
        return date instanceof Date && !isNaN(date) && date <= today;
    };

    // Show error message
    const showError = (elementId, message) => {
        const element = document.getElementById(elementId);
        if (element) {
            // Remove existing error styling
            element.classList.remove('is-valid');
            element.classList.add('is-invalid');
            
            // Create or update error message
            let errorElement = element.parentNode.querySelector('.invalid-feedback');
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'invalid-feedback';
                element.parentNode.appendChild(errorElement);
            }
            errorElement.textContent = message;
        }
    };

    // Clear error message
    const clearError = (elementId) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('is-invalid');
            element.classList.add('is-valid');
            
            const errorElement = element.parentNode.querySelector('.invalid-feedback');
            if (errorElement) {
                errorElement.remove();
            }
        }
    };

    // Show form message using Bootstrap alerts
    const showFormMessage = (message, type) => {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert.form-alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show form-alert`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert before the form
        if (form) {
            form.parentNode.insertBefore(alertDiv, form);
        }
    };

    // Form submission handler
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            let isValid = true;

            // Clear previous validation states
            const inputs = form.querySelectorAll('.form-control');
            inputs.forEach(input => {
                input.classList.remove('is-valid', 'is-invalid');
            });

            // Remove existing error messages
            const errorMessages = form.querySelectorAll('.invalid-feedback');
            errorMessages.forEach(msg => msg.remove());

            // Validate amount
            const amount = form.amount.value;
            if (!validateAmount(amount)) {
                showError('amount', 'Please enter a valid amount greater than 0');
                isValid = false;
            } else {
                clearError('amount');
            }

            // Validate source
            const source = form.source.value;
            if (!validateSource(source)) {
                showError('source', 'Please enter a valid source (1-100 characters)');
                isValid = false;
            } else {
                clearError('source');
            }

            // Validate date
            const date = form.date.value;
            if (!validateDate(date)) {
                showError('date', 'Please select a valid date (not in the future)');
                isValid = false;
            } else {
                clearError('date');
            }

            // Validate category
            const categoryId = form.category_id.value;
            if (!categoryId) {
                showError('category_id', 'Please select a category');
                isValid = false;
            } else {
                clearError('category_id');
            }

            if (!isValid) {
                showFormMessage('Please fix the errors below and try again.', 'error');
                return;
            }

            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Adding...';
            submitBtn.disabled = true;

            try {
                // Submit the form normally (let Flask handle it)
                form.submit();
                
            } catch (error) {
                console.error('Error:', error);
                showFormMessage('An error occurred. Please try again later.', 'error');
                
                // Restore button state
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });

        // Real-time validation
        const amountInput = form.querySelector('#amount');
        if (amountInput) {
            amountInput.addEventListener('input', () => {
                if (amountInput.value) {
                    if (!validateAmount(amountInput.value)) {
                        showError('amount', 'Please enter a valid amount greater than 0');
                    } else {
                        clearError('amount');
                    }
                }
            });

            // Format amount input
            amountInput.addEventListener('blur', () => {
                if (amountInput.value && validateAmount(amountInput.value)) {
                    amountInput.value = parseFloat(amountInput.value).toFixed(2);
                }
            });
        }

        const sourceInput = form.querySelector('#source');
        if (sourceInput) {
            sourceInput.addEventListener('input', () => {
                if (sourceInput.value) {
                    if (!validateSource(sourceInput.value)) {
                        showError('source', 'Please enter a valid source (1-100 characters)');
                    } else {
                        clearError('source');
                    }
                }
            });
        }

        const dateInputField = form.querySelector('#date');
        if (dateInputField) {
            dateInputField.addEventListener('change', () => {
                if (dateInputField.value) {
                    if (!validateDate(dateInputField.value)) {
                        showError('date', 'Please select a valid date (not in the future)');
                    } else {
                        clearError('date');
                    }
                }
            });
        }

        // Clear form handler
        form.addEventListener('reset', () => {
            // Clear all validation states
            const inputs = form.querySelectorAll('.form-control');
            inputs.forEach(input => {
                input.classList.remove('is-valid', 'is-invalid');
            });

            // Remove error messages
            const errorMessages = form.querySelectorAll('.invalid-feedback');
            errorMessages.forEach(msg => msg.remove());

            // Remove alerts
            const alerts = document.querySelectorAll('.alert.form-alert');
            alerts.forEach(alert => alert.remove());

            // Hide recurrence div
            if (recurrenceDiv) {
                recurrenceDiv.style.display = 'none';
            }

            // Reset date to today
            if (dateInput) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        });
    }

    // Modal event handlers
    const modal = document.getElementById('addIncomeModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', () => {
            // Reset form when modal is closed
            if (form) {
                form.reset();
            }
        });

        modal.addEventListener('shown.bs.modal', () => {
            // Focus on first input when modal opens
            const firstInput = modal.querySelector('.form-control');
            if (firstInput) {
                firstInput.focus();
            }
        });
    }
});

// Global functions for edit and delete (called from template)
function editIncome(incomeId) {
    // TODO: Implement edit functionality
    console.log('Edit income:', incomeId);
    alert('Edit functionality coming soon!');
}

function deleteIncome(incomeId) {
    if (confirm('Are you sure you want to delete this income record?')) {
        // Create a form to submit delete request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/income/delete/${incomeId}`;
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken.getAttribute('content');
            form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Custom event for income updates
window.addEventListener('incomeAdded', (event) => {
    console.log('Income added:', event.detail);
    // Refresh the page or update the table
    setTimeout(() => {
        window.location.reload();
    }, 1000);
});