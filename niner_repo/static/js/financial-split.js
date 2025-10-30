// State management
let financialState = {
    updateInterval: 5000, // Update every 5 seconds
    lastUpdate: null,
    costs: {
        total: 0,
        items: []
    },
    savings: {
        total: 0,
        items: []
    }
};

// Initialize when document loads
document.addEventListener('DOMContentLoaded', () => {
    initializeFinancialView();
    setupEventListeners();
});

// Initialize the financial view
async function initializeFinancialView() {
    await updateFinancialData();
    setInterval(updateFinancialData, financialState.updateInterval);
}

// Set up event listeners for real-time updates
function setupEventListeners() {
    // Listen for new income entries
    window.addEventListener('incomeAdded', async () => {
        await updateFinancialData();
    });

    // Listen for new expense entries
    window.addEventListener('expenseAdded', async () => {
        await updateFinancialData();
    });

    // Listen for income updates
    window.addEventListener('incomeUpdated', async () => {
        await updateFinancialData();
    });

    // Listen for expense updates
    window.addEventListener('expenseUpdated', async () => {
        await updateFinancialData();
    });
}

// Update financial data
async function updateFinancialData() {
    try {
        showLoading(true);
        
        // Fetch latest financial data
        const response = await fetch('/api/finance/summary');
        if (!response.ok) throw new Error('Failed to fetch financial data');
        
        const data = await response.json();
        
        // Update state
        updateState(data);
        
        // Update UI
        updateUI();
        
        financialState.lastUpdate = new Date();
        
    } catch (error) {
        console.error('Error updating financial data:', error);
        showError('Failed to update financial data');
    } finally {
        showLoading(false);
    }
}

// Update the state with new data
function updateState(data) {
    // Update costs
    financialState.costs = {
        total: data.summary.total_expenses,
        items: data.expenses_breakdown || []
    };
    
    // Update savings
    financialState.savings = {
        total: data.summary.total_savings,
        items: data.income_breakdown || []
    };
}

// Update the UI with current state
function updateUI() {
    const total = financialState.costs.total + financialState.savings.total;
    
    // Update costs side
    updateAmount('total-costs', financialState.costs.total);
    updatePercentage('costs-percentage', total, financialState.costs.total);
    updateProgress('costs-progress', total, financialState.costs.total);
    updateDetailsList('costs-list', financialState.costs.items);
    
    // Update savings side
    updateAmount('total-savings', financialState.savings.total);
    updatePercentage('savings-percentage', total, financialState.savings.total);
    updateProgress('savings-progress', total, financialState.savings.total);
    updateDetailsList('savings-list', financialState.savings.items);
}

// Update amount display with animation
function updateAmount(elementId, newValue) {
    const element = document.getElementById(elementId);
    const oldValue = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ''));
    
    if (oldValue !== newValue) {
        element.textContent = formatCurrency(newValue);
        element.parentElement.classList.add('amount-updated');
        
        setTimeout(() => {
            element.parentElement.classList.remove('amount-updated');
        }, 500);
    }
}

// Update percentage display
function updatePercentage(elementId, total, value) {
    const percentage = total > 0 ? (value / total) * 100 : 0;
    document.getElementById(elementId).textContent = formatPercentage(percentage);
}

// Update progress bar
function updateProgress(elementId, total, value) {
    const percentage = total > 0 ? (value / total) * 100 : 0;
    document.getElementById(elementId).style.width = `${percentage}%`;
}

// Update details list
function updateDetailsList(elementId, items) {
    const container = document.getElementById(elementId);
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

// Utility Functions
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

// Loading state management
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

// Error handling
function showError(message) {
    // Implement error notification system
    console.error(message);
    // You could add a toast notification system here
}