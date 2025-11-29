/**
 * Quick Expense Entry JavaScript
 * Handles form validation, auto-suggestions, and fast expense logging
 */

// Configuration
const CONFIG = {
    MAX_DESCRIPTION_LENGTH: 200,
    SUGGESTION_DELAY: 200, // ms
    TOAST_DURATION: 3000, // ms
    CATEGORY_KEYWORDS: {
        'Food': ['food', 'lunch', 'dinner', 'breakfast', 'restaurant', 'cafe', 'coffee', 'mcdonald', 'burger', 'pizza', 'grocery', 'market'],
        'Transportation': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'bus', 'train', 'metro', 'transport'],
        'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'concert', 'game', 'entertainment', 'theater'],
        'Shopping': ['amazon', 'walmart', 'target', 'mall', 'clothing', 'clothes', 'shoes', 'shopping'],
        'Health': ['pharmacy', 'doctor', 'hospital', 'medicine', 'health', 'gym', 'fitness'],
        'Utilities': ['electric', 'water', 'internet', 'phone', 'bill', 'utility'],
        'Education': ['book', 'course', 'tuition', 'school', 'education', 'class'],
        'Other': []
    }
};

// State
let debounceTimer = null;
let historicalExpenses = [];

// Performance metrics
const performance_metrics = {
    pageLoadTime: 0,
    formRenderTime: 0,
    suggestionResponseTimes: [],
    apiResponseTimes: []
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    const startTime = performance.now();
    
    initializeForm();
    loadRecentExpenses();

    setupEventListeners();
    setDefaultDate();
    
    // Record page load time
    const endTime = performance.now();
    performance_metrics.pageLoadTime = endTime - startTime;
    performance_metrics.formRenderTime = endTime - startTime;
    
    // Log performance metrics (only in development)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Quick Expense Performance Metrics:');
        console.log(`- Page Load Time: ${performance_metrics.pageLoadTime.toFixed(2)}ms`);
        console.log(`- Form Render Time: ${performance_metrics.formRenderTime.toFixed(2)}ms`);
    }
});

/**
 * Initialize form elements
 */
function initializeForm() {
    const amountInput = document.getElementById('amount');
    const categorySelect = document.getElementById('category');
    const descriptionInput = document.getElementById('description');
    const charCount = document.getElementById('charCount');
    
    // Focus on amount input
    if (amountInput) {
        amountInput.focus();
    }
    
    // Character counter for description
    if (descriptionInput && charCount) {
        descriptionInput.addEventListener('input', function() {
            charCount.textContent = this.value.length;
            if (this.value.length > CONFIG.MAX_DESCRIPTION_LENGTH - 20) {
                charCount.style.color = '#dc3545';
            } else {
                charCount.style.color = '#999';
            }
        });
    }
}

/**
 * Set default date to today
 */
function setDefaultDate() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    const form = document.getElementById('quickExpenseForm');
    const clearBtn = document.getElementById('clearBtn');
    const quickAmountBtns = document.querySelectorAll('.quick-amount-btn');
    const descriptionInput = document.getElementById('description');
    
    // Form submission
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', clearForm);
    }
    
    // Quick amount buttons
    quickAmountBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = this.dataset.amount;
            document.getElementById('amount').value = amount;
            validateAmount();
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        });
    });
    
    // Real-time validation
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', debounce(validateAmount, 300));
        amountInput.addEventListener('blur', validateAmount);
    }
    
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', validateCategory);
    }
    
    // Auto-suggestion on description change
    if (descriptionInput) {
        descriptionInput.addEventListener('input', debounce(suggestCategory, CONFIG.SUGGESTION_DELAY));
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            form.dispatchEvent(new Event('submit'));
        }
        
        // Escape to clear
        if (e.key === 'Escape') {
            clearForm();
        }
    });
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(debounceTimer);
            func(...args);
        };
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(later, wait);
    };
}

/**
 * Validate amount input
 */
function validateAmount() {
    const amountInput = document.getElementById('amount');
    const errorEl = document.getElementById('amountError');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!amountInput) return false;
    
    const amount = parseFloat(amountInput.value);
    
    // Clear previous error
    errorEl.textContent = '';
    amountInput.style.borderColor = '#e0e0e0';
    
    // Validation
    if (!amountInput.value) {
        errorEl.textContent = 'Amount is required';
        amountInput.style.borderColor = '#dc3545';
        submitBtn.disabled = true;
        return false;
    }
    
    if (isNaN(amount) || amount <= 0) {
        errorEl.textContent = 'Please enter a valid amount greater than 0';
        amountInput.style.borderColor = '#dc3545';
        submitBtn.disabled = true;
        return false;
    }
    
    if (amount > 999999) {
        errorEl.textContent = 'Amount is too large';
        amountInput.style.borderColor = '#dc3545';
        submitBtn.disabled = true;
        return false;
    }
    
    // Valid
    amountInput.style.borderColor = '#00703C';
    submitBtn.disabled = false;
    return true;
}

/**
 * Validate category selection
 */
function validateCategory() {
    const categorySelect = document.getElementById('category');
    const errorEl = document.getElementById('categoryError');
    
    if (!categorySelect) return false;
    
    // Clear previous error
    errorEl.textContent = '';
    categorySelect.style.borderColor = '#e0e0e0';
    
    if (!categorySelect.value) {
        errorEl.textContent = 'Please select a category';
        categorySelect.style.borderColor = '#dc3545';
        return false;
    }
    
    // Valid
    categorySelect.style.borderColor = '#00703C';
    return true;
}

/**
 * Auto-suggest category based on description
 */
function suggestCategory() {
    const suggestionStart = performance.now();
    
    const descriptionInput = document.getElementById('description');
    const categorySelect = document.getElementById('category');
    const suggestionEl = document.getElementById('categorySuggestion');
    
    if (!descriptionInput || !categorySelect || !suggestionEl) return;
    
    const description = descriptionInput.value.toLowerCase().trim();
    
    // Don't suggest if category already selected or description too short
    if (categorySelect.value || description.length < 3) {
        suggestionEl.classList.remove('show');
        return;
    }
    
    // Check historical data first
    const historicalMatch = findHistoricalMatch(description);
    if (historicalMatch) {
        showSuggestion(historicalMatch, 'Based on history');
        recordSuggestionTime(suggestionStart);
        return;
    }
    
    // Check keywords
    for (const [category, keywords] of Object.entries(CONFIG.CATEGORY_KEYWORDS)) {
        for (const keyword of keywords) {
            if (description.includes(keyword)) {
                showSuggestion(category, 'Suggested');
                recordSuggestionTime(suggestionStart);
                return;
            }
        }
    }
    
    // No match found
    suggestionEl.classList.remove('show');
    recordSuggestionTime(suggestionStart);
}

/**
 * Record suggestion response time
 */
function recordSuggestionTime(startTime) {
    const responseTime = performance.now() - startTime;
    performance_metrics.suggestionResponseTimes.push(responseTime);
    
    // Keep only last 10 measurements
    if (performance_metrics.suggestionResponseTimes.length > 10) {
        performance_metrics.suggestionResponseTimes.shift();
    }
    
    // Log if slow (development only)
    if ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && responseTime > 200) {
        console.warn(`Slow suggestion response: ${responseTime.toFixed(2)}ms`);
    }
}

/**
 * Find category from historical expenses
 */
function findHistoricalMatch(description) {
    if (!historicalExpenses.length) return null;
    
    // Find exact or partial match
    for (const expense of historicalExpenses) {
        if (expense.description && expense.description.toLowerCase().includes(description)) {
            return expense.category;
        }
    }
    
    return null;
}

/**
 * Show category suggestion
 */
function showSuggestion(category, label) {
    const categorySelect = document.getElementById('category');
    const suggestionEl = document.getElementById('categorySuggestion');
    
    if (!suggestionEl) return;
    
    suggestionEl.textContent = `${label}: ${category}`;
    suggestionEl.classList.add('show');
    
    // Click to apply suggestion
    suggestionEl.onclick = function() {
        categorySelect.value = category;
        validateCategory();
        suggestionEl.classList.remove('show');
    };
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        suggestionEl.classList.remove('show');
    }, 5000);
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Validate
    const isAmountValid = validateAmount();
    const isCategoryValid = validateCategory();
    
    if (!isAmountValid || !isCategoryValid) {
        return;
    }
    
    // Get form data
    const formData = {
        amount: parseFloat(document.getElementById('amount').value),
        category: document.getElementById('category').value,
        description: document.getElementById('description').value.trim() || '',
        date: document.getElementById('date').value
    };
    
    // Show loading state
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'flex';
    
    try {
        // Submit to API with timing
        const apiStart = performance.now();
        
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        // Record API response time
        const apiTime = performance.now() - apiStart;
        performance_metrics.apiResponseTimes.push(apiTime);
        
        // Keep only last 10 measurements
        if (performance_metrics.apiResponseTimes.length > 10) {
            performance_metrics.apiResponseTimes.shift();
        }
        
        // Log API performance (development only)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log(`API Response Time: ${apiTime.toFixed(2)}ms`);
        }
        
        if (response.ok && data.success) {
            // Success!
            showSuccessToast(formData);
            clearForm();
            loadRecentExpenses();
            
            // Trigger budget/analytics update
            triggerBudgetUpdate();
        } else {
            // Error from server
            showError(data.error || 'Failed to add expense');
        }
    } catch (error) {
        console.error('Error submitting expense:', error);
        showError('Network error. Please try again.');
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
}

/**
 * Show success toast notification
 */
function showSuccessToast(expense) {
    const toast = document.getElementById('successToast');
    const messageEl = toast.querySelector('.toast-message');
    
    if (!toast || !messageEl) return;
    
    messageEl.textContent = `$${expense.amount.toFixed(2)} added to ${expense.category}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, CONFIG.TOAST_DURATION);
}

/**
 * Show error message
 */
function showError(message) {
    alert(message); // Simple for now, can be improved with custom modal
}

/**
 * Clear form
 */
function clearForm() {
    const form = document.getElementById('quickExpenseForm');
    if (form) {
        form.reset();
        setDefaultDate();
        
        // Clear error messages
        document.getElementById('amountError').textContent = '';
        document.getElementById('categoryError').textContent = '';
        document.getElementById('charCount').textContent = '0';
        
        // Reset borders
        document.getElementById('amount').style.borderColor = '#e0e0e0';
        document.getElementById('category').style.borderColor = '#e0e0e0';
        
        // Hide suggestion
        document.getElementById('categorySuggestion').classList.remove('show');
        
        // Focus on amount
        document.getElementById('amount').focus();
    }
}

/**
 * Load recent expenses
 */
async function loadRecentExpenses() {
    try {
        const response = await fetch('/api/expenses/recent?limit=5');
        const data = await response.json();
        
        if (data.success && data.expenses) {
            historicalExpenses = data.expenses;
            renderRecentExpenses(data.expenses);
        }
    } catch (error) {
        console.error('Error loading recent expenses:', error);
    }
}

/**
 * Render recent expenses
 */
function renderRecentExpenses(expenses) {
    const listEl = document.getElementById('recentExpensesList');
    if (!listEl) return;
    
    if (!expenses || expenses.length === 0) {
        listEl.innerHTML = '<div class="empty-state">No recent expenses</div>';
        return;
    }
    
    listEl.innerHTML = expenses.map(expense => `
        <div class="recent-expense-item">
            <div class="recent-expense-info">
                <div class="recent-expense-category">${expense.category}</div>
                <div class="recent-expense-description">
                    ${expense.description || 'No description'}
                </div>
            </div>
            <div class="recent-expense-amount">$${parseFloat(expense.amount).toFixed(2)}</div>
        </div>
    `).join('');
}

/**
 * Trigger budget and analytics update
 */
function triggerBudgetUpdate() {
    // Trigger notification check
    fetch('/notifications/api/check-budget', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    }).catch(err => console.error('Error checking budget:', err));
    
    // Update notification badge
    if (typeof updateNotificationBadge === 'function') {
        updateNotificationBadge();
    }
    
    // Trigger dashboard refresh if on dashboard page
    if (window.location.pathname === '/dashboard' || window.location.pathname === '/') {
        // Dispatch custom event for dashboard to refresh
        window.dispatchEvent(new CustomEvent('expenseAdded', {
            detail: { source: 'quick-expense' }
        }));
    }
    
    // Trigger budget page refresh if on budget page
    if (window.location.pathname.includes('/budget')) {
        window.dispatchEvent(new CustomEvent('expenseAdded', {
            detail: { source: 'quick-expense' }
        }));
    }
}

