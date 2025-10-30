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
        name: document.getElementById('goalName').value,
        description: document.getElementById('goalDescription').value,
        target_amount: parseFloat(document.getElementById('targetAmount').value),
        current_amount: parseFloat(document.getElementById('currentAmount').value) || 0,
        target_date: document.getElementById('targetDate').value,
        category: document.getElementById('goalCategory').value,
        monthly_contribution: parseFloat(document.getElementById('monthlyContribution').value) || 0,
        created_date: new Date().toISOString().split('T')[0]
    };
    
    try {
        // For now, save to localStorage until backend is ready
        const goals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
        goalData.id = Date.now().toString();
        goals.push(goalData);
        localStorage.setItem('financialGoals', JSON.stringify(goals));
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('addGoalModal')).hide();
        
        // Reload goals
        await loadGoals();
        
        showNotification('Goal saved successfully!', 'success');
    } catch (error) {
        console.error('Error saving goal:', error);
        showNotification('Error saving goal. Please try again.', 'error');
    }
}

// Load goals
async function loadGoals() {
    try {
        // For now, load from localStorage until backend is ready
        const goals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
        financialState.goals = goals;
        displayGoals();
    } catch (error) {
        console.error('Error loading goals:', error);
        showNotification('Error loading goals.', 'error');
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
    
    // Set goal data
    cardElement.querySelector('.goal-card').setAttribute('data-goal-id', goal.id);
    cardElement.querySelector('.goal-icon').className = `goal-icon ${goal.category}`;
    cardElement.querySelector('.goal-icon-class').className = getCategoryIcon(goal.category);
    cardElement.querySelector('.goal-name').textContent = goal.name;
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
    const goal = financialState.goals.find(g => g.id === goalId);
    
    if (goal) {
        // Populate modal with existing data
        document.getElementById('goalName').value = goal.name;
        document.getElementById('goalDescription').value = goal.description || '';
        document.getElementById('targetAmount').value = goal.target_amount;
        document.getElementById('currentAmount').value = goal.current_amount;
        document.getElementById('targetDate').value = goal.target_date;
        document.getElementById('goalCategory').value = goal.category;
        document.getElementById('monthlyContribution').value = goal.monthly_contribution || 0;
        
        // Store goal ID for updating
        document.getElementById('addGoalModal').setAttribute('data-editing-goal-id', goalId);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('addGoalModal'));
        modal.show();
    }
}

// Add contribution
function addContribution(button) {
    const goalCard = button.closest('.goal-card');
    const goalId = goalCard.getAttribute('data-goal-id');
    const goal = financialState.goals.find(g => g.id === goalId);
    
    if (goal) {
        const contribution = prompt(`Add contribution to "${goal.name}":`, '0.00');
        if (contribution && !isNaN(contribution) && parseFloat(contribution) > 0) {
            goal.current_amount += parseFloat(contribution);
            
            // Save updated goal
            const goals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
            const goalIndex = goals.findIndex(g => g.id === goalId);
            if (goalIndex !== -1) {
                goals[goalIndex] = goal;
                localStorage.setItem('financialGoals', JSON.stringify(goals));
                displayGoals();
                showNotification(`$${contribution} added to ${goal.name}!`, 'success');
            }
        }
    }
}

// Delete goal
function deleteGoal(button) {
    const goalCard = button.closest('.goal-card');
    const goalId = goalCard.getAttribute('data-goal-id');
    const goal = financialState.goals.find(g => g.id === goalId);
    
    if (goal && confirm(`Are you sure you want to delete "${goal.name}"?`)) {
        const goals = JSON.parse(localStorage.getItem('financialGoals') || '[]');
        const filteredGoals = goals.filter(g => g.id !== goalId);
        localStorage.setItem('financialGoals', JSON.stringify(filteredGoals));
        loadGoals();
        showNotification(`${goal.name} deleted successfully.`, 'success');
    }
}

// Update financial data (existing function)
async function updateFinancialData() {
    try {
        showLoading(true);
        
        // Mock data for now
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
    // Simple alert for now - you could implement a toast system
    if (type === 'error') {
        alert('Error: ' + message);
    } else {
        alert(message);
    }
}

// Export functions to global scope
window.showAddGoalModal = showAddGoalModal;
window.saveGoal = saveGoal;
window.editGoal = editGoal;
window.addContribution = addContribution;
window.deleteGoal = deleteGoal;