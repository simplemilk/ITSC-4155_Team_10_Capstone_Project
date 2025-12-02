/**
 * Budget Planning JavaScript
 * Handles budget creation, management, and interactive features
 */

// Global variables
let monthlyIncome = 0;
let currentBudget = null;
let expenses = {};

// Initialize budget functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeBudgetForm();
    initializeFilterTabs();
    initializeBudgetCards();
    loadBudgetData();
    initializeBudgetCreateForm(); // New function for budget-create.html
});

/**
 * Initialize the budget creation form (for budget-create.html)
 */
function initializeBudgetCreateForm() {
    const totalAmountInput = document.getElementById('total_amount');
    const budgetInputs = document.querySelectorAll('.budget-input');
    const submitBtn = document.getElementById('submit-btn');
    const budgetCreateForm = document.getElementById('budgetCreateForm');
    
    if (!totalAmountInput || !budgetCreateForm) {
        return; // Not on budget-create page
    }
    
    // Update calculations when inputs change
    totalAmountInput.addEventListener('input', updateBudgetCreateCalculations);
    budgetInputs.forEach(input => {
        input.addEventListener('input', updateBudgetCreateCalculations);
    });
    
    // Form submission
    budgetCreateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const totalBudget = parseFloat(totalAmountInput.value) || 0;
        const totalAllocated = Array.from(budgetInputs).reduce((sum, input) => {
            return sum + (parseFloat(input.value) || 0);
        }, 0);
        
        if (Math.abs(totalBudget - totalAllocated) > 0.01) {
            alert('Total allocated amount must equal the total budget amount.');
            return;
        }
        
        // Submit the form
        this.submit();
    });
}

/**
 * Update budget creation calculations
 */
function updateBudgetCreateCalculations() {
    const totalAmount = parseFloat(document.getElementById('total_amount')?.value) || 0;
    const budgetInputs = document.querySelectorAll('.budget-input');
    const percentageDisplays = document.querySelectorAll('.percentage-display');
    
    let totalAllocated = 0;
    
    // Calculate totals and percentages
    budgetInputs.forEach((input, index) => {
        const value = parseFloat(input.value) || 0;
        totalAllocated += value;
        
        const percentage = totalAmount > 0 ? (value / totalAmount * 100) : 0;
        if (percentageDisplays[index]) {
            percentageDisplays[index].textContent = `${percentage.toFixed(1)}%`;
        }
        
        // Add validation classes
        if (value > 0 && totalAmount > 0) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else if (totalAmount > 0) {
            input.classList.remove('is-valid', 'is-invalid');
        }
    });
    
    // Update summary
    const remaining = totalAmount - totalAllocated;
    const allocationPercentage = totalAmount > 0 ? (totalAllocated / totalAmount * 100) : 0;
    
    const totalAllocatedEl = document.getElementById('total-allocated');
    const budgetAmountEl = document.getElementById('budget-amount');
    const remainingAmountEl = document.getElementById('remaining-amount');
    
    if (totalAllocatedEl) totalAllocatedEl.textContent = `$${totalAllocated.toFixed(2)}`;
    if (budgetAmountEl) budgetAmountEl.textContent = `$${totalAmount.toFixed(2)}`;
    if (remainingAmountEl) remainingAmountEl.textContent = `$${remaining.toFixed(2)}`;
    
    // Update progress bar
    const progressBar = document.getElementById('allocation-progress');
    const statusText = document.getElementById('allocation-status');
    
    if (progressBar && statusText) {
        progressBar.style.width = `${Math.min(allocationPercentage, 100)}%`;
        
        if (totalAmount === 0) {
            progressBar.className = 'progress-bar';
            statusText.textContent = 'Enter your budget to see allocation';
        } else if (remaining === 0) {
            progressBar.className = 'progress-bar bg-success';
            statusText.textContent = 'Perfect allocation!';
        } else if (remaining > 0) {
            progressBar.className = 'progress-bar bg-warning';
            statusText.textContent = `$${remaining.toFixed(2)} remaining to allocate`;
        } else {
            progressBar.className = 'progress-bar bg-danger';
            statusText.textContent = `Over budget by $${Math.abs(remaining).toFixed(2)}`;
        }
    }
    
    // Update submit button
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        if (totalAmount > 0 && Math.abs(remaining) < 0.01) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-secondary');
            submitBtn.classList.add('btn-niner-green');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.remove('btn-niner-green');
            submitBtn.classList.add('btn-secondary');
        }
    }
}

/**
 * Apply budget preset
 */
function applyPreset(type) {
    const totalAmount = parseFloat(document.getElementById('total_amount')?.value) || 0;
    
    if (totalAmount === 0) {
        alert('Please enter a total budget amount first.');
        return;
    }
    
    let distribution;
    
    switch(type) {
        case 'conservative':
            distribution = { food: 0.5, transportation: 0.25, entertainment: 0.1, other: 0.15 };
            break;
        case 'balanced':
            distribution = { food: 0.4, transportation: 0.3, entertainment: 0.15, other: 0.15 };
            break;
        case 'flexible':
            distribution = { food: 0.35, transportation: 0.25, entertainment: 0.25, other: 0.15 };
            break;
        default:
            return;
    }
    
    // Apply distribution
    const foodBudget = document.getElementById('food_budget');
    const transportBudget = document.getElementById('transportation_budget');
    const entertainmentBudget = document.getElementById('entertainment_budget');
    const otherBudget = document.getElementById('other_budget');
    
    if (foodBudget) foodBudget.value = (totalAmount * distribution.food).toFixed(2);
    if (transportBudget) transportBudget.value = (totalAmount * distribution.transportation).toFixed(2);
    if (entertainmentBudget) entertainmentBudget.value = (totalAmount * distribution.entertainment).toFixed(2);
    if (otherBudget) otherBudget.value = (totalAmount * distribution.other).toFixed(2);
    
    updateBudgetCreateCalculations();
}

/**
 * Get budget suggestions from API
 */
async function getSuggestions() {
    try {
        const response = await fetch('/budget/api/suggestions');
        if (response.ok) {
            const suggestions = await response.json();
            
            if (suggestions.total > 0) {
                const totalAmountInput = document.getElementById('total_amount');
                const foodBudget = document.getElementById('food_budget');
                const transportBudget = document.getElementById('transportation_budget');
                const entertainmentBudget = document.getElementById('entertainment_budget');
                const otherBudget = document.getElementById('other_budget');
                
                if (totalAmountInput) totalAmountInput.value = suggestions.total.toFixed(2);
                if (suggestions.Food && foodBudget) foodBudget.value = suggestions.Food.toFixed(2);
                if (suggestions.Transportation && transportBudget) transportBudget.value = suggestions.Transportation.toFixed(2);
                if (suggestions.Entertainment && entertainmentBudget) entertainmentBudget.value = suggestions.Entertainment.toFixed(2);
                if (suggestions.Other && otherBudget) otherBudget.value = suggestions.Other.toFixed(2);
                
                updateBudgetCreateCalculations();
                
                alert('Budget suggestions applied based on your spending history!');
            } else {
                alert('No spending history found. Add some transactions first to get suggestions.');
            }
        }
    } catch (error) {
        console.error('Error getting suggestions:', error);
        alert('Unable to get suggestions at this time.');
    }
}

/**
 * Initialize the budget creation form (for modal)
 */
function initializeBudgetForm() {
    const totalBudgetInput = document.getElementById('totalBudget');
    const budgetInputs = document.querySelectorAll('.budget-input');
    const budgetSlider = document.getElementById('budgetSlider');
    const budgetSummary = document.getElementById('budgetSummary');
    
    if (!totalBudgetInput || !budgetSlider || !budgetSummary) {
        console.log('Budget form elements not found, skipping initialization');
        return;
    }
    
    // Get monthly income from template (if available)
    const incomeElement = document.querySelector('[data-monthly-income]');
    if (incomeElement) {
        monthlyIncome = parseFloat(incomeElement.dataset.monthlyIncome) || 0;
    }
    
    // Set recommended budget based on income
    if (monthlyIncome > 0) {
        const recommendedWeekly = (monthlyIncome * 0.25 / 4).toFixed(2);
        totalBudgetInput.placeholder = `Recommended: $${recommendedWeekly}`;
        
        // Auto-fill with recommended amount
        totalBudgetInput.value = recommendedWeekly;
        distributeBudget();
    }
    
    // Update budget distribution when slider changes
    budgetSlider.addEventListener('input', function() {
        distributeBudget();
    });
    
    // Update summary when inputs change
    budgetInputs.forEach(input => {
        input.addEventListener('input', updateBudgetSummary);
    });
    
    totalBudgetInput.addEventListener('input', function() {
        updateBudgetSummary();
        if (this.value) {
            distributeBudget();
        }
    });
    
    // Handle form submission
    const createBudgetForm = document.getElementById('createBudgetForm');
    if (createBudgetForm) {
        createBudgetForm.addEventListener('submit', handleBudgetSubmission);
    }
    
    // Initialize summary
    updateBudgetSummary();
}

/**
 * Distribute budget based on slider value and total budget
 */
function distributeBudget() {
    const budgetSlider = document.getElementById('budgetSlider');
    const totalBudgetInput = document.getElementById('totalBudget');
    
    if (!budgetSlider || !totalBudgetInput) return;
    
    const value = parseInt(budgetSlider.value);
    const total = parseFloat(totalBudgetInput.value) || 0;
    
    if (total > 0) {
        let distribution;
        
        if (value < 33) { // Conservative
            distribution = { 
                food: 0.5, 
                transportation: 0.25, 
                entertainment: 0.1, 
                other: 0.15 
            };
        } else if (value < 67) { // Balanced
            distribution = { 
                food: 0.4, 
                transportation: 0.3, 
                entertainment: 0.15, 
                other: 0.15 
            };
        } else { // Flexible
            distribution = { 
                food: 0.35, 
                transportation: 0.25, 
                entertainment: 0.25, 
                other: 0.15 
            };
        }
        
        // Update input fields
        const foodBudget = document.getElementById('foodBudget');
        const transportBudget = document.getElementById('transportBudget');
        const entertainmentBudget = document.getElementById('entertainmentBudget');
        const otherBudget = document.getElementById('otherBudget');
        
        if (foodBudget) foodBudget.value = (total * distribution.food).toFixed(2);
        if (transportBudget) transportBudget.value = (total * distribution.transportation).toFixed(2);
        if (entertainmentBudget) entertainmentBudget.value = (total * distribution.entertainment).toFixed(2);
        if (otherBudget) otherBudget.value = (total * distribution.other).toFixed(2);
        
        updateBudgetSummary();
        
        // Update slider label
        updateSliderLabel(value);
    }
}

/**
 * Update slider label based on current value
 */
function updateSliderLabel(value) {
    const sliderLabels = document.querySelector('.slider-labels');
    if (!sliderLabels) return;
    
    // Remove existing active class
    sliderLabels.querySelectorAll('small').forEach(label => {
        label.classList.remove('active');
    });
    
    // Add active class to current selection
    let activeIndex = 1; // Default to middle (Balanced)
    if (value < 33) activeIndex = 0; // Conservative
    else if (value > 67) activeIndex = 2; // Flexible
    
    const labels = sliderLabels.querySelectorAll('small');
    if (labels[activeIndex]) {
        labels[activeIndex].classList.add('active');
    }
}

/**
 * Update budget summary display
 */
function updateBudgetSummary() {
    const budgetInputs = document.querySelectorAll('.budget-input');
    const totalBudgetInput = document.getElementById('totalBudget');
    const budgetSummary = document.getElementById('budgetSummary');
    
    if (!budgetSummary) return;
    
    const total = Array.from(budgetInputs).reduce((sum, input) => {
        return sum + (parseFloat(input.value) || 0);
    }, 0);
    
    const totalBudget = parseFloat(totalBudgetInput?.value) || 0;
    const remaining = totalBudget - total;
    
    let summaryHTML = `Total allocated: $${total.toFixed(2)}`;
    
    if (totalBudget > 0) {
        summaryHTML += ` | Remaining: $${remaining.toFixed(2)}`;
        
        if (remaining < 0) {
            summaryHTML += ' <span class="text-danger">(Over budget!)</span>';
        } else if (remaining > 0) {
            summaryHTML += ' <span class="text-success">(Under budget)</span>';
        } else {
            summaryHTML += ' <span class="text-info">(Perfect allocation)</span>';
        }
    }
    
    budgetSummary.innerHTML = summaryHTML;
    
    // Update form validation
    updateFormValidation(remaining >= 0);
}

/**
 * Update form validation state
 */
function updateFormValidation(isValid) {
    const submitButton = document.querySelector('#createBudgetForm button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = !isValid;
        if (!isValid) {
            submitButton.classList.add('btn-outline-danger');
            submitButton.classList.remove('btn-primary');
        } else {
            submitButton.classList.remove('btn-outline-danger');
            submitButton.classList.add('btn-primary');
        }
    }
}

/**
 * Handle budget form submission
 */
async function handleBudgetSubmission(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Show loading state
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Budget...';
    submitButton.disabled = true;
    
    try {
        const formData = new FormData(form);
        const budgetData = Object.fromEntries(formData.entries());
        
        // Convert strings to numbers
        for (let key in budgetData) {
            budgetData[key] = parseFloat(budgetData[key]);
        }
        
        // Add metadata
        budgetData.created_at = new Date().toISOString();
        budgetData.week_start = getCurrentWeekStart();
        
        const response = await fetch('/budget/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(budgetData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showSuccess('Budget created successfully!');
            
            // Close modal and refresh page
            const modal = bootstrap.Modal.getInstance(document.getElementById('createBudgetModal'));
            if (modal) modal.hide();
            
            setTimeout(() => {
                location.reload();
            }, 1000);
            
        } else {
            throw new Error(result.error || 'Failed to create budget');
        }
        
    } catch (error) {
        console.error('Error creating budget:', error);
        showError('Error creating budget: ' + error.message);
    } finally {
        // Restore button state
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

/**
 * Initialize filter tabs for budget categories
 */
function initializeFilterTabs() {
    const filterTabs = document.querySelectorAll('.filter-tab');
    
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            filterTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Get filter value
            const filter = this.dataset.filter;
            
            // Apply filter
            applyBudgetFilter(filter);
        });
    });
}

/**
 * Apply budget filter
 */
function applyBudgetFilter(filter) {
    const budgetItems = document.querySelectorAll('.budget-category-card');
    
    budgetItems.forEach(item => {
        const category = item.classList.contains('food-category') ? 'food' :
                        item.classList.contains('transportation-category') ? 'transportation' :
                        item.classList.contains('entertainment-category') ? 'entertainment' :
                        'other';
        
        let shouldShow = true;
        
        switch(filter) {
            case 'over-budget':
                const statusElement = item.querySelector('.budget-status');
                shouldShow = statusElement && statusElement.classList.contains('over-budget');
                break;
            case 'under-budget':
                const statusElement2 = item.querySelector('.budget-status');
                shouldShow = statusElement2 && statusElement2.classList.contains('under-budget');
                break;
            case 'high-spend':
                const spentElement = item.querySelector('.spent');
                const spent = parseFloat(spentElement?.textContent.replace('$', '') || 0);
                shouldShow = spent > 50; // Adjust threshold as needed
                break;
            case 'all':
            default:
                shouldShow = true;
                break;
        }
        
        if (shouldShow) {
            item.style.display = 'block';
            item.classList.add('fade-in');
        } else {
            item.style.display = 'none';
            item.classList.remove('fade-in');
        }
    });
}

/**
 * Initialize budget cards with interactive features
 */
function initializeBudgetCards() {
    const budgetCards = document.querySelectorAll('.budget-category-card');
    
    budgetCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Add click handler for detailed view
        card.addEventListener('click', function() {
            const category = this.classList.contains('food-category') ? 'food' :
                            this.classList.contains('transportation-category') ? 'transportation' :
                            this.classList.contains('entertainment-category') ? 'entertainment' :
                            'other';
            
            showCategoryDetails(category);
        });
    });
}

/**
 * Show detailed view for a budget category
 */
function showCategoryDetails(category) {
    // This could open a modal or navigate to a detailed view
    console.log(`Showing details for ${category} category`);
    
    // For now, just show an alert with category info
    const categoryData = expenses[category] || 0;
    alert(`${category.toUpperCase()} Category\nSpent: $${categoryData.toFixed(2)}`);
}

/**
 * Load budget data from server
 */
async function loadBudgetData() {
    try {
        const response = await fetch('/budget/api/current');
        if (response.ok) {
            const data = await response.json();
            currentBudget = data.budget;
            expenses = data.expenses || {};
            monthlyIncome = data.monthly_income || 0;
            
            updateBudgetDisplay();
        }
    } catch (error) {
        console.error('Error loading budget data:', error);
    }
}

/**
 * Update budget display with current data
 */
function updateBudgetDisplay() {
    // Update overview cards
    updateOverviewCards();
    
    // Update progress bars
    updateProgressBars();
    
    // Update suggestions
    updateBudgetSuggestions();
}

/**
 * Update overview cards with current data
 */
function updateOverviewCards() {
    const totalBudgetCard = document.querySelector('.total-budget .budget-amount');
    const totalSpentCard = document.querySelector('.total-spent .budget-amount');
    const remainingBudgetCard = document.querySelector('.remaining-budget .budget-amount');
    const monthlyIncomeCard = document.querySelector('.monthly-income .budget-amount');
    
    if (totalBudgetCard && currentBudget) {
        totalBudgetCard.textContent = `$${currentBudget.total_budget?.toFixed(2) || '0.00'}`;
    }
    
    if (totalSpentCard) {
        const totalSpent = Object.values(expenses).reduce((sum, amount) => sum + amount, 0);
        totalSpentCard.textContent = `$${totalSpent.toFixed(2)}`;
    }
    
    if (remainingBudgetCard && currentBudget) {
        const totalBudget = currentBudget.total_budget || 0;
        const totalSpent = Object.values(expenses).reduce((sum, amount) => sum + amount, 0);
        const remaining = totalBudget - totalSpent;
        remainingBudgetCard.textContent = `$${remaining.toFixed(2)}`;
    }
    
    if (monthlyIncomeCard) {
        monthlyIncomeCard.textContent = `$${monthlyIncome.toFixed(2)}`;
    }
}

/**
 * Update progress bars for each category
 */
function updateProgressBars() {
    const categories = ['food', 'transportation', 'entertainment', 'other'];
    
    categories.forEach(category => {
        const card = document.querySelector(`.${category}-category`);
        if (!card || !currentBudget) return;
        
        const spent = expenses[category] || 0;
        const budget = currentBudget[`${category}_budget`] || 0;
        const percentage = budget > 0 ? (spent / budget * 100) : 0;
        
        const progressBar = card.querySelector('.progress-bar');
        const spentElement = card.querySelector('.spent');
        const budgetElement = card.querySelector('.budget');
        const statusElement = card.querySelector('.budget-status');
        
        if (progressBar) {
            progressBar.style.width = `${Math.min(percentage, 100)}%`;
        }
        
        if (spentElement) {
            spentElement.textContent = `$${spent.toFixed(2)}`;
        }
        
        if (budgetElement) {
            budgetElement.textContent = `/ $${budget.toFixed(2)}`;
        }
        
        if (statusElement) {
            if (spent > budget) {
                statusElement.textContent = 'Over Budget';
                statusElement.className = 'budget-status over-budget';
            } else {
                statusElement.textContent = 'On Track';
                statusElement.className = 'budget-status under-budget';
            }
        }
    });
}

/**
 * Update budget suggestions based on spending patterns
 */
function updateBudgetSuggestions() {
    // This would typically fetch data from the server
    // For now, we'll use placeholder logic
    console.log('Updating budget suggestions...');
}

/**
 * Get current week start date
 */
function getCurrentWeekStart() {
    const today = new Date();
    const day = today.getDay() || 7; // Make Sunday = 7
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - day + 1);
    return weekStart.toISOString().split('T')[0];
}

/**
 * Utility Functions
 */

// Show success message
function showSuccess(message) {
    showToast(message, 'success');
}

// Show error message
function showError(message) {
    showToast(message, 'error');
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
        </div>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

/**
 * Exported Functions for Button Handlers
 */

// Generate budget report
function generateBudgetReport() {
    showToast('Generating budget report...', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        showSuccess('Budget report generated successfully!');
        
        // Create downloadable CSV
        const csvContent = generateBudgetCSV();
        downloadCSV(csvContent, 'budget-report.csv');
    }, 1500);
}

// Generate CSV content for budget report
function generateBudgetCSV() {
    const headers = ['Category', 'Budget', 'Spent', 'Remaining', 'Status'];
    const categories = ['food', 'transportation', 'entertainment', 'other'];
    
    let csvContent = headers.join(',') + '\n';
    
    categories.forEach(category => {
        const budget = currentBudget ? currentBudget[`${category}_budget`] || 0 : 0;
        const spent = expenses[category] || 0;
        const remaining = budget - spent;
        const status = spent > budget ? 'Over Budget' : 'On Track';
        
        const row = [
            category.charAt(0).toUpperCase() + category.slice(1),
            budget.toFixed(2),
            spent.toFixed(2),
            remaining.toFixed(2),
            status
        ];
        
        csvContent += row.join(',') + '\n';
    });
    
    return csvContent;
}

// Download CSV file
function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Adjust current budget
function adjustBudget() {
    const modal = new bootstrap.Modal(document.getElementById('createBudgetModal'));
    modal.show();
    
    // Pre-fill form with current budget data if available
    if (currentBudget) {
        setTimeout(() => {
            const totalBudgetInput = document.getElementById('totalBudget');
            const foodBudget = document.getElementById('foodBudget');
            const transportBudget = document.getElementById('transportBudget');
            const entertainmentBudget = document.getElementById('entertainmentBudget');
            const otherBudget = document.getElementById('otherBudget');
            
            if (totalBudgetInput) totalBudgetInput.value = currentBudget.total_budget || '';
            if (foodBudget) foodBudget.value = currentBudget.food_budget || '';
            if (transportBudget) transportBudget.value = currentBudget.transportation_budget || '';
            if (entertainmentBudget) entertainmentBudget.value = currentBudget.entertainment_budget || '';
            if (otherBudget) otherBudget.value = currentBudget.other_budget || '';
            
            updateBudgetSummary();
        }, 100);
    }
}

// Copy last week's budget
function copyLastWeek() {
    showToast('Copying last week\'s budget...', 'info');
    
    // This would typically fetch last week's budget from the server
    setTimeout(() => {
        showSuccess('Last week\'s budget copied successfully!');
        // You would then populate the form or create a new budget
    }, 1000);
}

// Set budget alerts
function setBudgetAlerts() {
    showToast('Budget alerts feature coming soon!', 'info');
}

// Export functions to global scope for button handlers
window.generateBudgetReport = generateBudgetReport;
window.adjustBudget = adjustBudget;
window.copyLastWeek = copyLastWeek;
window.setBudgetAlerts = setBudgetAlerts;
window.applyPreset = applyPreset;
window.getSuggestions = getSuggestions;