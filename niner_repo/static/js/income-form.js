document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('income-form');
    const formMessage = document.getElementById('form-message');

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
        return date instanceof Date && !isNaN(date) && date <= today;
    };

    // Show error message
    const showError = (elementId, message) => {
        const errorElement = document.getElementById(`${elementId}-error`);
        errorElement.textContent = message;
        document.getElementById(elementId).classList.add('error');
    };

    // Clear error message
    const clearError = (elementId) => {
        const errorElement = document.getElementById(`${elementId}-error`);
        errorElement.textContent = '';
        document.getElementById(elementId).classList.remove('error');
    };

    // Show form message
    const showFormMessage = (message, type) => {
        formMessage.textContent = message;
        formMessage.className = `form-message ${type}`;
    };

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        let isValid = true;

        // Clear previous messages
        formMessage.className = 'form-message';
        formMessage.textContent = '';

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

        if (!isValid) return;

        try {
            const response = await fetch('/api/income', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: parseFloat(amount),
                    source: source,
                    description: form.description.value,
                    date: date
                })
            });

            const data = await response.json();

            if (response.ok) {
                showFormMessage('Income successfully recorded!', 'success');
                form.reset();
                // Emit custom event for parent components to update
                window.dispatchEvent(new CustomEvent('incomeAdded', { detail: data }));
            } else {
                showFormMessage(data.error || 'Failed to record income. Please try again.', 'error');
            }
        } catch (error) {
            showFormMessage('An error occurred. Please try again later.', 'error');
            console.error('Error:', error);
        }
    });

    // Real-time validation
    form.amount.addEventListener('input', () => {
        if (form.amount.value) {
            if (!validateAmount(form.amount.value)) {
                showError('amount', 'Please enter a valid amount greater than 0');
            } else {
                clearError('amount');
            }
        }
    });

    form.source.addEventListener('input', () => {
        if (form.source.value) {
            if (!validateSource(form.source.value)) {
                showError('source', 'Please enter a valid source (1-100 characters)');
            } else {
                clearError('source');
            }
        }
    });

    // Clear form handler
    form.addEventListener('reset', () => {
        // Clear all error messages
        ['amount', 'source', 'date'].forEach(clearError);
        formMessage.className = 'form-message';
        formMessage.textContent = '';
    });
});