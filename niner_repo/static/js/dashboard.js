// Dashboard state management
let dashboardState = {
    incomeChart: null,
    updateInterval: 30000, // 30 seconds
    lastUpdate: null
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    setupEventListeners();
});

async function initializeDashboard() {
    try {
        await Promise.all([
            updateFinancialOverview(),
            updateIncomeBreakdown(),
            updateBudgetStatus(),
            updateRecentActivity(),
            updateProjections()
        ]);
        
        // Set up periodic updates
        setInterval(updateDashboard, dashboardState.updateInterval);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load dashboard data. Please refresh the page.');
    }
}

// Event listeners for real-time updates
function setupEventListeners() {
    // Listen for income changes
    window.addEventListener('incomeAdded', () => {
        updateDashboard();
    });

    // Listen for expense changes
    window.addEventListener('expenseAdded', () => {
        updateDashboard();
    });

    // Listen for budget changes
    window.addEventListener('budgetUpdated', () => {
        updateDashboard();
    });
}

// Update all dashboard components
async function updateDashboard() {
    try {
        await Promise.all([
            updateFinancialOverview(),
            updateIncomeBreakdown(),
            updateBudgetStatus(),
            updateRecentActivity(),
            updateProjections()
        ]);
        dashboardState.lastUpdate = new Date();
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Financial Overview Updates
async function updateFinancialOverview() {
    try {
        const response = await fetch('/api/finance/summary');
        if (!response.ok) throw new Error('Failed to fetch financial summary');
        
        const data = await response.json();
        
        // Update overview cards
        document.getElementById('total-income').textContent = 
            formatCurrency(data.summary.total_income);
        document.getElementById('total-expenses').textContent = 
            formatCurrency(data.summary.total_expenses);
        document.getElementById('total-savings').textContent = 
            formatCurrency(data.summary.total_savings);
        document.getElementById('savings-rate').textContent = 
            formatPercentage(data.summary.savings_rate);
            
    } catch (error) {
        console.error('Error updating financial overview:', error);
        showError('Failed to update financial overview');
    }
}

// Income Breakdown Updates
async function updateIncomeBreakdown() {
    try {
        const response = await fetch('/api/finance/summary');
        if (!response.ok) throw new Error('Failed to fetch income breakdown');
        
        const data = await response.json();
        updateIncomeChart(data.income_breakdown);
        updateIncomeList(data.income_breakdown);
    } catch (error) {
        console.error('Error updating income breakdown:', error);
        showError('Failed to update income breakdown');
    }
}

// Update Income Chart
function updateIncomeChart(data) {
    const ctx = document.getElementById('income-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (dashboardState.incomeChart) {
        dashboardState.incomeChart.destroy();
    }
    
    // Create new chart
    dashboardState.incomeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.total),
                backgroundColor: generateColors(data.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Update Income List
function updateIncomeList(data) {
    const container = document.getElementById('income-breakdown');
    const template = document.getElementById('income-item-template');
    
    container.innerHTML = '';
    
    data.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        clone.querySelector('.category-name').textContent = item.category;
        clone.querySelector('.entry-count').textContent = 
            `${item.count} entries`;
        clone.querySelector('.amount').textContent = 
            formatCurrency(item.total);
        clone.querySelector('.average').textContent = 
            formatCurrency(item.average);
            
        container.appendChild(clone);
    });
}

// Budget Status Updates
async function updateBudgetStatus() {
    try {
        const response = await fetch('/api/finance/summary');
        if (!response.ok) throw new Error('Failed to fetch budget status');
        
        const data = await response.json();
        const container = document.getElementById('budget-status');
        const template = document.getElementById('budget-item-template');
        
        container.innerHTML = '';
        
        data.budget_allocations.forEach(item => {
            const clone = template.content.cloneNode(true);
            const usagePercentage = (item.spent_amount / item.allocated_amount) * 100;
            
            clone.querySelector('.category-name').textContent = item.category_name;
            clone.querySelector('.progress-fill').style.width = 
                `${Math.min(usagePercentage, 100)}%`;
            clone.querySelector('.spent-amount').textContent = 
                formatCurrency(item.spent_amount);
            clone.querySelector('.allocated-amount').textContent = 
                formatCurrency(item.allocated_amount);
                
            // Add color coding based on usage
            const progressFill = clone.querySelector('.progress-fill');
            if (usagePercentage > 90) {
                progressFill.style.backgroundColor = '#dc3545'; // Red
            } else if (usagePercentage > 75) {
                progressFill.style.backgroundColor = '#ffc107'; // Yellow
            }
            
            container.appendChild(clone);
        });
    } catch (error) {
        console.error('Error updating budget status:', error);
        showError('Failed to update budget status');
    }
}

// Recent Activity Updates
async function updateRecentActivity() {
    try {
        // Fetch both income and expense activity
        const [incomeResponse, expenseResponse] = await Promise.all([
            fetch('/api/income/?limit=10'),
            fetch('/api/expenses/?limit=10')
        ]);
        
        if (!incomeResponse.ok || !expenseResponse.ok) {
            throw new Error('Failed to fetch recent activity');
        }
        
        const incomeData = await incomeResponse.json();
        const expenseData = await expenseResponse.json();
        
        // Combine and sort activity
        const activity = [
            ...incomeData.data.map(item => ({
                ...item,
                type: 'income',
                date: new Date(item.date)
            })),
            ...expenseData.data.map(item => ({
                ...item,
                type: 'expense',
                date: new Date(item.date)
            }))
        ].sort((a, b) => b.date - a.date).slice(0, 10);
        
        updateActivityList(activity);
    } catch (error) {
        console.error('Error updating recent activity:', error);
        showError('Failed to update recent activity');
    }
}

// Update Activity List
function updateActivityList(activity) {
    const container = document.getElementById('recent-activity');
    const template = document.getElementById('activity-item-template');
    
    container.innerHTML = '';
    
    activity.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        clone.querySelector('.activity-icon').innerHTML = 
            item.type === 'income' ? '↑' : '↓';
        clone.querySelector('.activity-title').textContent = item.source;
        clone.querySelector('.activity-amount').textContent = 
            `${item.type === 'income' ? '+' : '-'}${formatCurrency(item.amount)}`;
        clone.querySelector('.activity-date').textContent = 
            formatDate(item.date);
            
        // Add color coding
        const amountElement = clone.querySelector('.activity-amount');
        amountElement.style.color = item.type === 'income' ? '#28a745' : '#dc3545';
        
        container.appendChild(clone);
    });
}

// Projections Updates
async function updateProjections() {
    try {
        const response = await fetch('/api/finance/savings/projected');
        if (!response.ok) throw new Error('Failed to fetch projections');
        
        const data = await response.json();
        
        // Update monthly projections
        const monthlyContainer = document.getElementById('monthly-projection');
        monthlyContainer.innerHTML = `
            <div class="projection-row">
                <span>Income:</span>
                <span>${formatCurrency(data.monthly.income)}</span>
            </div>
            <div class="projection-row">
                <span>Expenses:</span>
                <span>${formatCurrency(data.monthly.expenses)}</span>
            </div>
            <div class="projection-row total">
                <span>Projected Savings:</span>
                <span>${formatCurrency(data.monthly.savings)}</span>
            </div>
        `;
        
        // Update annual projections
        const annualContainer = document.getElementById('annual-projection');
        annualContainer.innerHTML = `
            <div class="projection-row">
                <span>Income:</span>
                <span>${formatCurrency(data.annual.income)}</span>
            </div>
            <div class="projection-row">
                <span>Expenses:</span>
                <span>${formatCurrency(data.annual.expenses)}</span>
            </div>
            <div class="projection-row total">
                <span>Projected Savings:</span>
                <span>${formatCurrency(data.annual.savings)}</span>
            </div>
        `;
    } catch (error) {
        console.error('Error updating projections:', error);
        showError('Failed to update projections');
    }
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

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    }).format(new Date(date));
}

function generateColors(count) {
    const colors = [
        '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336',
        '#009688', '#3F51B5', '#FFC107', '#795548', '#607D8B'
    ];
    
    if (count <= colors.length) {
        return colors.slice(0, count);
    }
    
    // Generate additional colors if needed
    const additional = count - colors.length;
    for (let i = 0; i < additional; i++) {
        colors.push(`hsl(${Math.random() * 360}, 70%, 50%)`);
    }
    
    return colors;
}

function showError(message) {
    // Implement error notification system
    console.error(message);
    // You could add a toast notification system here
}