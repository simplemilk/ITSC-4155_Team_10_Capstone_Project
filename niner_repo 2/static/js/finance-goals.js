// State management
let financialState = {
    updateInterval: 5000,
    lastUpdate: null,
    costs: { total: 0, items: [] },
    savings: { total: 0, items: [] },
    goals: []
};

// Initialize when document loads
document.addEventListener('DOMContentLoaded', () => {
    initializeFinancialView();
    setupEventListeners();
    setupModalEventListeners();
});

// Initialize the financial view
async function initializeFinancialView() {
    await updateFinancialData();
    await loadGoals();
    setInterval(updateFinancialData, financialState.updateInterval);
}

// Set up event listeners
function setupEventListeners() {
    window.addEventListener('incomeAdded', async () => await updateFinancialData());
    window.addEventListener('expenseAdded', async () => await updateFinancialData());
    window.addEventListener('incomeUpdated', async () => await updateFinancialData());
    window.addEventListener('expenseUpdated', async () => await updateFinancialData());
}

// Set up modal event listeners
function setupModalEventListeners() {
    const targetAmountInput = document.getElementById('targetAmount');
    const targetDateInput = document.getElementById('targetDate');
    const monthlyContributionInput = document.getElementById('monthlyContribution');
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    targetDateInput.min = today;
    
    // Calculate recommended monthly contribution
    const updateContributionHelp = () => {
        const targetAmount = parseFloat(targetAmountInput.value) || 0;
        const currentAmount = parseFloat(document.getElementById('currentAmount').value) || 0;
        const targetDate = new Date(targetDateInput.value);
        const today = new Date();
        
        if (targetAmount > 0 && targetDate > today) {
            const monthsLeft = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24 * 30));
            const amountNeeded = targetAmount - currentAmount;
            const monthlyNeeded = Math.max(0, amountNeeded / monthsLeft);
            
            document.getElementById('contributionHelp').textContent = 
                `Recommended: $${monthlyNeeded.toFixed(2)} per month (${monthsLeft} months)`;
        } else {
            document.getElementById('contributionHelp').textContent = '';
        }
    };
    
    targetAmountInput.addEventListener('input', updateContributionHelp);
    targetDateInput.addEventListener('change', updateContributionHelp);
    document.getElementById('currentAmount').addEventListener('input', updateContributionHelp);
}

// Show add goal modal
function showAddGoalModal() {
    const modal = new bootstrap.Modal(document.getElementById('addGoalModal'));
    
    // Reset form
    document.getElementById('addGoalForm').reset();
    document.getElementById('contributionHelp').textContent = '';
    
    // Remove editing state
    document.getElementById('addGoalModal').removeAttribute('data-editing-goal-id');
    
    // Set default date to 1 year from now
    const defaultDate = new Date();
    defaultDate.setFullYear(defaultDate.getFullYear() + 1);
    document.getElementById('targetDate').value = defaultDate.toISOString().split('T')[0];
    
    modal.show();
}

// Save goal
async function saveGoal() {
    const form = document.getElementById('addGoalForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const goalData = {
        goal_name: document.getElementById('goalName').value,
        description: document.getElementById('goalDescription').value,
        target_amount: parseFloat(document.getElementById('targetAmount').value),
        current_amount: parseFloat(document.getElementById('currentAmount').value) || 0,
        target_date: document.getElementById('targetDate').value,
        category: document.getElementById('goalCategory').value
    };
    
    try {
        const editingId = document.getElementById('addGoalModal').getAttribute('data-editing-goal-id');
        
        let response;
        if (editingId) {
            // Update existing goal
            response = await fetch(`/api/goals/${editingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(goalData)
            });
        } else {
            // Create new goal
            response = await fetch('/api/goals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(goalData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('addGoalModal')).hide();
            
            // Reload goals
            await loadGoals();
            
            showNotification(result.message, 'success');
        } else {
            showNotification(result.error || 'Error saving goal', 'error');
        }
    } catch (error) {
        console.error('Error saving goal:', error);
        showNotification('Error saving goal. Please try again.', 'error');
    }
}

// Load goals from API
async function loadGoals() {
    try {
        const response = await fetch('/api/goals');
        const data = await response.json();
        
        if (data.goals) {
            financialState.goals = data.goals;
            displayGoals();
        } else {
            throw new Error(data.error || 'Failed to load goals');
        }
    } catch (error) {
        console.error('Error loading goals:', error);
        showNotification('Error loading goals.', 'error');
        
        // Fallback to localStorage for demo purposes
        const localGoals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
        financialState.goals = localGoals;
        displayGoals();
    }
}

// Display goals
function displayGoals() {
    const container = document.getElementById('goals-grid');
    const template = document.getElementById('goal-card-template');
    
    // Clear existing goals except loading message
    const existingCards = container.querySelectorAll('.goal-card');
    existingCards.forEach(card => card.remove());
    
    if (financialState.goals.length === 0) {
        container.innerHTML = `
            <div class="loading-message">
                <i class="fas fa-target me-2"></i>
                No goals yet. Create your first financial goal to get started!
            </div>
        `;
        return;
    }
    
    // Remove loading message
    const loadingMessage = container.querySelector('.loading-message');
    if (loadingMessage) loadingMessage.remove();
    
    financialState.goals.forEach(goal => {
        const clone = template.content.cloneNode(true);
        populateGoalCard(clone, goal);
        container.appendChild(clone);
    });
}

// Populate goal card with data
function populateGoalCard(cardElement, goal) {
    const progress = (goal.current_amount / goal.target_amount) * 100;
    const today = new Date();
    const targetDate = new Date(goal.target_date);
    const daysLeft = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
    const monthsLeft = Math.ceil(daysLeft / 30);
    const amountNeeded = goal.target_amount - goal.current_amount;
    const monthlyNeeded = monthsLeft > 0 ? amountNeeded / monthsLeft : 0;
    
    // Set goal data - use goal_name for API data, name for localStorage data
    const goalName = goal.goal_name || goal.name;
    
    cardElement.querySelector('.goal-card').setAttribute('data-goal-id', goal.id);
    cardElement.querySelector('.goal-icon').className = `goal-icon ${goal.category}`;
    cardElement.querySelector('.goal-icon-class').className = getCategoryIcon(goal.category);
    cardElement.querySelector('.goal-name').textContent = goalName;
    cardElement.querySelector('.goal-description').textContent = goal.description || 'No description';
    
    // Progress information
    cardElement.querySelector('.current-amount').textContent = `$${formatCurrency(goal.current_amount)}`;
    cardElement.querySelector('.target-amount').textContent = `/ $${formatCurrency(goal.target_amount)}`;
    cardElement.querySelector('.goal-progress-bar').style.width = `${Math.min(progress, 100)}%`;
    cardElement.querySelector('.progress-percentage').textContent = `${progress.toFixed(1)}% Complete`;
    
    // Timeline information
    cardElement.querySelector('.target-date').textContent = formatDate(goal.target_date);
    cardElement.querySelector('.days-left').textContent = daysLeft > 0 ? `${daysLeft} days` : 'Overdue';
    cardElement.querySelector('.monthly-need').textContent = monthlyNeeded > 0 ? `$${formatCurrency(monthlyNeeded)}` : '$0.00';
    
    // Status badge
    const statusBadge = cardElement.querySelector('.status-badge');
    const status = getGoalStatus(goal, daysLeft, progress);
    statusBadge.textContent = status.text;
    statusBadge.className = `status-badge ${status.class}`;
}

// Get category icon
function getCategoryIcon(category) {
    const icons = {
        emergency: 'fas fa-shield-alt',
        education: 'fas fa-graduation-cap',
        travel: 'fas fa-plane',
        technology: 'fas fa-laptop',
        housing: 'fas fa-home',
        transportation: 'fas fa-car',
        other: 'fas fa-star'
    };
    return icons[category] || icons.other;
}

// Get goal status
function getGoalStatus(goal, daysLeft, progress) {
    if (progress >= 100) {
        return { text: 'Completed', class: 'completed' };
    } else if (daysLeft < 0) {
        return { text: 'Overdue', class: 'urgent' };
    } else if (daysLeft <= 30) {
        return { text: 'Urgent', class: 'urgent' };
    } else if (progress < 25 && daysLeft <= 90) {
        return { text: 'Behind', class: 'behind' };
    } else {
        return { text: 'On Track', class: 'on-track' };
    }
}

// Edit goal
function editGoal(button) {
    const goalCard = button.closest('.goal-card');
    const goalId = goalCard.getAttribute('data-goal-id');
    const goal = financialState.goals.find(g => g.id == goalId);
    
    if (goal) {
        // Populate modal with existing data
        document.getElementById('goalName').value = goal.goal_name || goal.name;
        document.getElementById('goalDescription').value = goal.description || '';
        document.getElementById('targetAmount').value = goal.target_amount;
        document.getElementById('currentAmount').value = goal.current_amount;
        document.getElementById('targetDate').value = goal.target_date;
        document.getElementById('goalCategory').value = goal.category;
        
        // Store goal ID for updating
        document.getElementById('addGoalModal').setAttribute('data-editing-goal-id', goalId);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('addGoalModal'));
        modal.show();
    }
}

// Add contribution
async function addContribution(button) {
    const goalCard = button.closest('.goal-card');
    const goalId = goalCard.getAttribute('data-goal-id');
    const goal = financialState.goals.find(g => g.id == goalId);
    
    if (goal) {
        const goalName = goal.goal_name || goal.name;
        const contribution = prompt(`Add contribution to "${goalName}":`, '0.00');
        if (contribution && !isNaN(contribution) && parseFloat(contribution) > 0) {
            const newAmount = goal.current_amount + parseFloat(contribution);
            
            try {
                const response = await fetch(`/api/goals/${goalId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ...goal,
                        current_amount: newAmount
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    await loadGoals();
                    showNotification(`$${contribution} added to ${goalName}!`, 'success');
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Error adding contribution:', error);
                showNotification('Error adding contribution. Please try again.', 'error');
            }
        }
    }
}

// Delete goal
async function deleteGoal(button) {
    const goalCard = button.closest('.goal-card');
    const goalId = goalCard.getAttribute('data-goal-id');
    const goal = financialState.goals.find(g => g.id == goalId);
    
    if (goal) {
        const goalName = goal.goal_name || goal.name;
        if (confirm(`Are you sure you want to delete "${goalName}"?`)) {
            try {
                const response = await fetch(`/api/goals/${goalId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    await loadGoals();
                    showNotification(`${goalName} deleted successfully.`, 'success');
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Error deleting goal:', error);
                showNotification('Error deleting goal. Please try again.', 'error');
            }
        }
    }
}

// Update financial data (existing function)
async function updateFinancialData() {
    try {
        showLoading(true);
        
        // Mock data for now - you can replace this with real API calls
        const mockData = {
            summary: {
                total_expenses: 1450.75,
                total_savings: 1399.25
            },
            expenses_breakdown: [
                { category: 'Food & Dining', amount: 345.50 },
                { category: 'Transportation', amount: 125.25 },
                { category: 'Entertainment', amount: 89.00 }
            ],
            income_breakdown: [
                { category: 'Part-time Job', amount: 800.00 },
                { category: 'Financial Aid', amount: 599.25 }
            ]
        };
        
        updateState(mockData);
        updateUI();
        financialState.lastUpdate = new Date();
        
    } catch (error) {
        console.error('Error updating financial data:', error);
        showError('Failed to update financial data');
    } finally {
        showLoading(false);
    }
}

// Update state with new data
function updateState(data) {
    financialState.costs = {
        total: data.summary.total_expenses,
        items: data.expenses_breakdown || []
    };
    
    financialState.savings = {
        total: data.summary.total_savings,
        items: data.income_breakdown || []
    };
}

// Update UI with current state
function updateUI() {
    const total = financialState.costs.total + financialState.savings.total;
    
    updateAmount('total-costs', financialState.costs.total);
    updatePercentage('costs-percentage', total, financialState.costs.total);
    updateProgress('costs-progress', total, financialState.costs.total);
    updateDetailsList('costs-list', financialState.costs.items);
    
    updateAmount('total-savings', financialState.savings.total);
    updatePercentage('savings-percentage', total, financialState.savings.total);
    updateProgress('savings-progress', total, financialState.savings.total);
    updateDetailsList('savings-list', financialState.savings.items);
}

// Utility functions
function updateAmount(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (element) {
        const oldValue = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
        if (oldValue !== newValue) {
            element.textContent = formatCurrency(newValue);
            element.parentElement.classList.add('amount-updated');
            setTimeout(() => {
                element.parentElement.classList.remove('amount-updated');
            }, 500);
        }
    }
}

function updatePercentage(elementId, total, value) {
    const element = document.getElementById(elementId);
    if (element) {
        const percentage = total > 0 ? (value / total) * 100 : 0;
        element.textContent = formatPercentage(percentage);
    }
}

function updateProgress(elementId, total, value) {
    const element = document.getElementById(elementId);
    if (element) {
        const percentage = total > 0 ? (value / total) * 100 : 0;
        element.style.width = `${percentage}%`;
    }
}

function updateDetailsList(elementId, items) {
    const container = document.getElementById(elementId);
    if (container) {
        container.innerHTML = '';
        items.forEach(item => {
            const detailItem = document.createElement('div');
            detailItem.className = 'detail-item';
            detailItem.innerHTML = `
                <span class="detail-label">${item.category || item.name}</span>
                <span class="detail-value">$${formatCurrency(item.amount || item.total)}</span>
            `;
            container.appendChild(detailItem);
        });
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading(show) {
    const sides = document.querySelectorAll('.split-side');
    sides.forEach(side => {
        if (show) {
            side.classList.add('loading');
        } else {
            side.classList.remove('loading');
        }
    });
}

function showError(message) {
    console.error(message);
    showNotification(message, 'error');
}

function showNotification(message, type = 'info') {
    // Create a toast notification
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}

// Export functions to global scope
window.showAddGoalModal = showAddGoalModal;
window.saveGoal = saveGoal;
window.editGoal = editGoal;
window.addContribution = addContribution;
window.deleteGoal = deleteGoal;