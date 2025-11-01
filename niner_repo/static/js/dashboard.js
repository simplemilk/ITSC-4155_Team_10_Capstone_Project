/**
 * Dashboard JavaScript
 * Handles dashboard data loading, updates, and interactions
 */

// Dashboard state management
let dashboardState = {
    incomeChart: null,
    updateInterval: 30000, // 30 seconds
    lastUpdate: null,
    isLoading: false
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    initializeDashboard();
    setupEventListeners();
});

/**
 * Initialize all dashboard components
 */
async function initializeDashboard() {
    try {
        dashboardState.isLoading = true;
        
        // Show loading state
        showLoadingState();
        
        // Load all dashboard data
        await Promise.all([
            updateFinancialOverview(),
            updateIncomeBreakdown(), 
            updateBudgetStatus(),
            updateRecentActivity()
        ]);
        
        // Set up periodic updates
        setInterval(updateDashboard, dashboardState.updateInterval);
        
        dashboardState.lastUpdate = new Date();
        console.log('Dashboard initialized successfully');
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load dashboard data. Please refresh the page.');
    } finally {
        dashboardState.isLoading = false;
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Listen for data changes
    window.addEventListener('incomeAdded', updateDashboard);
    window.addEventListener('expenseAdded', updateDashboard);
    window.addEventListener('budgetUpdated', updateDashboard);
    
    // Refresh button handler
    const refreshBtn = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
}

/**
 * Update all dashboard components
 */
async function updateDashboard() {
    if (dashboardState.isLoading) return;
    
    try {
        dashboardState.isLoading = true;
        
        await Promise.all([
            updateFinancialOverview(),
            updateIncomeBreakdown(),
            updateBudgetStatus(), 
            updateRecentActivity()
        ]);
        
        dashboardState.lastUpdate = new Date();
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
        showError('Failed to update dashboard data');
    } finally {
        dashboardState.isLoading = false;
    }
}

/**
 * Update financial overview section
 */
async function updateFinancialOverview() {
    try {
        // For now, use mock data until backend API is ready
        const mockData = {
            summary: {
                total_income: 2850.00,
                total_expenses: 1450.75,
                total_savings: 1399.25,
                savings_rate: 49.0
            }
        };
        
        // Update overview cards with animation
        animateValueUpdate('total-income', mockData.summary.total_income);
        animateValueUpdate('total-expenses', mockData.summary.total_expenses);
        animateValueUpdate('total-savings', mockData.summary.total_savings);
        animateValueUpdate('savings-rate', mockData.summary.savings_rate);
        
        console.log('Financial overview updated');
        
    } catch (error) {
        console.error('Error updating financial overview:', error);
        
        // Set default values on error
        document.getElementById('total-income').textContent = '0.00';
        document.getElementById('total-expenses').textContent = '0.00';
        document.getElementById('total-savings').textContent = '0.00';
        document.getElementById('savings-rate').textContent = '0';
    }
}

/**
 * Update income breakdown section
 */
async function updateIncomeBreakdown() {
    try {
        // Mock income data
        const mockIncomeData = [
            { category: 'Part-time Job', total: 1200.00, count: 4, average: 300.00 },
            { category: 'Financial Aid', total: 800.00, count: 1, average: 800.00 },
            { category: 'Family Support', total: 500.00, count: 2, average: 250.00 },
            { category: 'Freelance Work', total: 350.00, count: 3, average: 116.67 }
        ];
        
        updateIncomeChart(mockIncomeData);
        updateIncomeList(mockIncomeData);
        
        console.log('Income breakdown updated');
        
    } catch (error) {
        console.error('Error updating income breakdown:', error);
        showIncomeError();
    }
}

/**
 * Update income chart
 */
function updateIncomeChart(data) {
    const ctx = document.getElementById('income-chart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (dashboardState.incomeChart) {
        dashboardState.incomeChart.destroy();
    }
    
    // Create new chart
    dashboardState.incomeChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.total),
                backgroundColor: generateColors(data.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = formatCurrency(context.parsed);
                            const percentage = ((context.parsed / data.reduce((sum, item) => sum + item.total, 0)) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

/**
 * Update income list
 */
function updateIncomeList(data) {
    const container = document.getElementById('income-breakdown');
    const template = document.getElementById('income-item-template');
    
    if (!container || !template) return;
    
    container.innerHTML = '';
    
    data.forEach((item, index) => {
        const clone = template.content.cloneNode(true);
        
        clone.querySelector('.category-name').textContent = item.category;
        clone.querySelector('.entry-count').textContent = `${item.count} entries`;
        clone.querySelector('.amount').textContent = formatCurrency(item.total);
        clone.querySelector('.average').textContent = formatCurrency(item.average);
        
        // Add animation delay
        const itemElement = clone.querySelector('.income-item');
        itemElement.style.animationDelay = `${index * 0.1}s`;
        itemElement.classList.add('fade-in');
        
        container.appendChild(clone);
    });
}

/**
 * Update budget status section
 */
async function updateBudgetStatus() {
    try {
        // Mock budget data
        const mockBudgetData = [
            { category_name: 'Food & Dining', spent_amount: 245.50, allocated_amount: 300.00, icon: 'fas fa-utensils' },
            { category_name: 'Transportation', spent_amount: 85.25, allocated_amount: 150.00, icon: 'fas fa-car' },
            { category_name: 'Entertainment', spent_amount: 120.00, allocated_amount: 100.00, icon: 'fas fa-film' },
            { category_name: 'Other', spent_amount: 65.75, allocated_amount: 80.00, icon: 'fas fa-ellipsis-h' }
        ];
        
        const container = document.getElementById('budget-status');
        const template = document.getElementById('budget-item-template');
        
        if (!container || !template) return;
        
        container.innerHTML = '';
        
        mockBudgetData.forEach((item, index) => {
            const clone = template.content.cloneNode(true);
            const usagePercentage = (item.spent_amount / item.allocated_amount) * 100;
            
            clone.querySelector('.category-icon').className = item.icon;
            clone.querySelector('.category-name').textContent = item.category_name;
            clone.querySelector('.progress-fill').style.width = `${Math.min(usagePercentage, 100)}%`;
            clone.querySelector('.spent-amount').textContent = formatCurrency(item.spent_amount);
            clone.querySelector('.allocated-amount').textContent = formatCurrency(item.allocated_amount);
            
            // Add status text and color coding
            const statusElement = clone.querySelector('.budget-status');
            const progressFill = clone.querySelector('.progress-fill');
            
            if (usagePercentage > 100) {
                statusElement.textContent = 'Over Budget';
                statusElement.style.color = '#dc3545';
                progressFill.style.background = 'linear-gradient(90deg, #dc3545, #c82333)';
            } else if (usagePercentage > 90) {
                statusElement.textContent = 'Nearly Full';
                statusElement.style.color = '#ffc107';
                progressFill.style.background = 'linear-gradient(90deg, #ffc107, #e0a800)';
            } else {
                statusElement.textContent = 'On Track';
                statusElement.style.color = '#28a745';
            }
            
            // Add animation delay
            const itemElement = clone.querySelector('.budget-item');
            itemElement.style.animationDelay = `${index * 0.15}s`;
            itemElement.classList.add('slide-in');
            
            container.appendChild(clone);
        });
        
        console.log('Budget status updated');
        
    } catch (error) {
        console.error('Error updating budget status:', error);
        showBudgetError();
    }
}

/**
 * Update recent activity section
 */
async function updateRecentActivity() {
    try {
        // Mock activity data
        const mockActivity = [
            { source: 'Starbucks Coffee', amount: 5.75, type: 'expense', date: new Date(Date.now() - 2 * 60 * 60 * 1000) },
            { source: 'Part-time Job', amount: 125.00, type: 'income', date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) },
            { source: 'Gas Station', amount: 32.50, type: 'expense', date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) },
            { source: 'Family Transfer', amount: 200.00, type: 'income', date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000) },
            { source: 'Textbook Purchase', amount: 89.99, type: 'expense', date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) },
            { source: 'Movie Theater', amount: 15.50, type: 'expense', date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) }
        ];
        
        updateActivityList(mockActivity);
        console.log('Recent activity updated');
        
    } catch (error) {
        console.error('Error updating recent activity:', error);
        showActivityError();
    }
}

/**
 * Update activity list
 */
function updateActivityList(activity) {
    const container = document.getElementById('recent-activity');
    const template = document.getElementById('activity-item-template');
    
    if (!container || !template) return;
    
    container.innerHTML = '';
    
    activity.forEach((item, index) => {
        const clone = template.content.cloneNode(true);
        
        const iconElement = clone.querySelector('.activity-icon');
        iconElement.innerHTML = item.type === 'income' ? '↗' : '↙';
        iconElement.style.backgroundColor = item.type === 'income' ? '#d4edda' : '#f8d7da';
        iconElement.style.color = item.type === 'income' ? '#28a745' : '#dc3545';
        
        clone.querySelector('.activity-title').textContent = item.source;
        
        const amountElement = clone.querySelector('.activity-amount');
        amountElement.textContent = `${item.type === 'income' ? '+' : '-'}$${formatCurrency(item.amount)}`;
        amountElement.style.color = item.type === 'income' ? '#28a745' : '#dc3545';
        
        clone.querySelector('.activity-date').textContent = formatDate(item.date);
        
        // Add animation delay
        const itemElement = clone.querySelector('.activity-item');
        itemElement.style.animationDelay = `${index * 0.1}s`;
        itemElement.classList.add('fade-in');
        
        container.appendChild(clone);
    });
}

/**
 * Show loading state for all sections
 */
function showLoadingState() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    });
}

/**
 * Error handlers
 */
function showIncomeError() {
    const container = document.getElementById('income-breakdown');
    if (container) {
        container.innerHTML = '<div class="text-center text-muted py-3">Unable to load income data</div>';
    }
}

function showBudgetError() {
    const container = document.getElementById('budget-status');
    if (container) {
        container.innerHTML = '<div class="text-center text-muted py-3">Unable to load budget data</div>';
    }
}

function showActivityError() {
    const container = document.getElementById('recent-activity');
    if (container) {
        container.innerHTML = '<div class="text-center text-muted py-3">Unable to load recent activity</div>';
    }
}

/**
 * Utility Functions
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(Math.abs(amount));
}

function formatDate(date) {
    const now = new Date();
    const diffInHours = (now - new Date(date)) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
        return 'Just now';
    } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 48) {
        return 'Yesterday';
    } else {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric'
        }).format(new Date(date));
    }
}

function generateColors(count) {
    const colors = [
        '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336',
        '#009688', '#3F51B5', '#FFC107', '#795548', '#607D8B'
    ];
    
    return colors.slice(0, count);
}

function animateValueUpdate(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = parseFloat(element.textContent) || 0;
    const step = (newValue - currentValue) / 20;
    let current = currentValue;
    
    const animate = () => {
        current += step;
        if ((step > 0 && current >= newValue) || (step < 0 && current <= newValue)) {
            current = newValue;
            element.textContent = elementId.includes('rate') ? 
                current.toFixed(1) : current.toFixed(2);
            return;
        }
        
        element.textContent = elementId.includes('rate') ? 
            current.toFixed(1) : current.toFixed(2);
        requestAnimationFrame(animate);
    };
    
    requestAnimationFrame(animate);
}

function showError(message) {
    console.error(message);
    // You can implement a toast notification system here
}

/**
 * Button Handlers (exported to global scope)
 */
function refreshDashboard() {
    console.log('Refreshing dashboard...');
    updateDashboard();
}

function showAddIncomeModal() {
    console.log('Show add income modal');
    window.location.href = '/income';
}

function showAddExpenseModal() {
    console.log('Show add expense modal');
    window.location.href = '/transactions';
}

function viewBudget() {
    console.log('View budget');
    window.location.href = '/budget';
}

function generateReport() {
    console.log('Generate report');
    alert('Report generation feature coming soon!');
}

function addGoal() {
    console.log('Add financial goal');
    alert('Financial goals feature coming soon!');
}

function viewFinancialGoals() {
    console.log('View financial goals');
    window.location.href = '/finance-goals';
}

// Export functions to global scope
window.refreshDashboard = refreshDashboard;
window.showAddIncomeModal = showAddIncomeModal;
window.showAddExpenseModal = showAddExpenseModal;
window.viewBudget = viewBudget;
window.generateReport = generateReport;
window.addGoal = addGoal;