/**
 * Transaction Page JavaScript
 * Handles filtering, interactions, and dynamic content for the transaction page
 */

class TransactionManager {
    constructor() {
        this.transactions = [];
        this.filteredTransactions = [];
        this.currentFilter = 'all';
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadTransactions();
        this.initializeModals();
        this.startAutoRefresh();
    }
    
    bindEvents() {
        // Filter tab events
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.handleFilterChange(e));
        });
        
        // Quick add expense buttons
        document.querySelectorAll('[onclick^="addExpense"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const category = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.showAddExpenseModal(category);
            });
        });
        
        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });
        
        // Export button
        const exportBtn = document.querySelector('[onclick="exportTransactions()"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportTransactions();
            });
        }
        
        // Generate report button
        const reportBtn = document.querySelector('[onclick="generateReport()"]');
        if (reportBtn) {
            reportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.generateReport();
            });
        }
        
        // Search functionality
        this.initializeSearch();
        
        // Keyboard shortcuts
        this.initializeKeyboardShortcuts();
    }
    
    loadTransactions() {
        const transactionItems = document.querySelectorAll('.transaction-item');
        this.transactions = Array.from(transactionItems).map(item => ({
            element: item,
            type: item.dataset.type,
            category: item.dataset.category,
            description: item.querySelector('.transaction-description').textContent.trim(),
            amount: parseFloat(item.querySelector('.transaction-amount').textContent.replace(/[^0-9.-]/g, '')),
            date: this.parseDateFromElement(item),
            meta: item.querySelector('.transaction-meta').textContent.trim()
        }));
        
        this.filteredTransactions = [...this.transactions];
    }
    
    parseDateFromElement(item) {
        const metaText = item.querySelector('.transaction-meta').textContent;
        const dateMatch = metaText.match(/(\w+ \d+, \d+)/);
        return dateMatch ? new Date(dateMatch[1]) : new Date();
    }
    
    handleFilterChange(e) {
        const tab = e.target.closest('.filter-tab');
        if (!tab) return;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Apply filter
        const filter = tab.dataset.filter;
        this.currentFilter = filter;
        this.applyFilter(filter);
    }
    
    applyFilter(filter) {
        const now = new Date();
        const sevenDaysAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
        
        this.transactions.forEach(transaction => {
            let show = false;
            
            switch(filter) {
                case 'all':
                    show = true;
                    break;
                case 'expenses':
                    show = transaction.type === 'expense';
                    break;
                case 'income':
                    show = transaction.type === 'income';
                    break;
                case 'recent':
                    show = transaction.date >= sevenDaysAgo;
                    break;
                default:
                    show = transaction.category === filter;
            }
            
            this.animateTransactionVisibility(transaction.element, show);
        });
        
        // Update filtered transactions array
        this.filteredTransactions = this.transactions.filter(t => 
            t.element.style.display !== 'none'
        );
        
        // Show/hide empty state
        this.updateEmptyState();
        
        // Update URL without page reload
        this.updateURL(filter);
    }
    
    animateTransactionVisibility(element, show) {
        if (show) {
            element.classList.remove('filtering-out');
            element.style.display = 'flex';
            setTimeout(() => element.classList.add('fade-in'), 10);
        } else {
            element.classList.add('filtering-out');
            setTimeout(() => {
                element.style.display = 'none';
                element.classList.remove('fade-in');
            }, 300);
        }
    }
    
    updateEmptyState() {
        const visibleTransactions = this.transactions.filter(t => 
            t.element.style.display !== 'none'
        );
        
        const transactionsList = document.getElementById('transactions-list');
        const existingEmptyState = transactionsList.querySelector('.empty-state');
        
        if (visibleTransactions.length === 0) {
            if (!existingEmptyState) {
                this.showEmptyState();
            }
        } else {
            if (existingEmptyState) {
                existingEmptyState.remove();
            }
        }
    }
    
    showEmptyState() {
        const filterText = this.getFilterDisplayText(this.currentFilter);
        const transactionsList = document.getElementById('transactions-list');
        
        const emptyStateHTML = `
            <div class="empty-state slide-in">
                <div class="empty-state-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h5>No ${filterText} found</h5>
                <p>Try adjusting your filter or add some ${this.currentFilter === 'income' ? 'income' : 'expenses'}.</p>
                ${this.currentFilter !== 'income' ? `
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addExpenseModal">
                        <i class="fas fa-plus me-2"></i>Add ${filterText}
                    </button>
                ` : `
                    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addIncomeModal">
                        <i class="fas fa-plus me-2"></i>Add Income
                    </button>
                `}
            </div>
        `;
        
        transactionsList.innerHTML = emptyStateHTML;
    }
    
    getFilterDisplayText(filter) {
        const filterMap = {
            'all': 'transactions',
            'expenses': 'expenses',
            'income': 'income',
            'recent': 'recent transactions',
            'food': 'food expenses',
            'transportation': 'transportation expenses',
            'entertainment': 'entertainment expenses',
            'other': 'other expenses'
        };
        
        return filterMap[filter] || 'transactions';
    }
    
    updateURL(filter) {
        const url = new URL(window.location);
        if (filter === 'all') {
            url.searchParams.delete('filter');
        } else {
            url.searchParams.set('filter', filter);
        }
        window.history.replaceState({}, '', url);
    }
    
    showAddExpenseModal(category = '') {
        const modal = new bootstrap.Modal(document.getElementById('addExpenseModal'));
        if (category) {
            document.getElementById('expense-category').value = category;
        }
        modal.show();
        
        // Focus on description field
        setTimeout(() => {
            document.getElementById('expense-description').focus();
        }, 500);
    }
    
    showAddIncomeModal() {
        const modal = new bootstrap.Modal(document.getElementById('addIncomeModal'));
        modal.show();
        
        // Focus on source field
        setTimeout(() => {
            document.getElementById('income-source').focus();
        }, 500);
    }
    
    handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!this.validateForm(form)) {
            e.preventDefault();
            return;
        }
        
        this.showLoadingState(submitBtn);
        
        // Allow form to submit naturally, but provide user feedback
        setTimeout(() => {
            this.showToast('Transaction is being saved...', 'info');
        }, 100);
    }
    
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        // Validate amount fields
        const amountFields = form.querySelectorAll('input[type="number"]');
        amountFields.forEach(field => {
            const value = parseFloat(field.value);
            if (isNaN(value) || value <= 0) {
                this.showFieldError(field, 'Please enter a valid amount greater than 0');
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    showLoadingState(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner me-2"></span>Saving...';
        button.disabled = true;
        
        // Store original text for restoration
        button.dataset.originalText = originalText;
    }
    
    restoreButtonState(button) {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
            delete button.dataset.originalText;
        }
    }
    
    exportTransactions() {
        this.showToast('Preparing export...', 'info');
        
        // Simulate export process
        setTimeout(() => {
            const filteredData = this.filteredTransactions.map(t => ({
                date: t.date.toLocaleDateString(),
                type: t.type,
                category: t.category,
                description: t.description,
                amount: t.amount
            }));
            
            this.downloadCSV(filteredData, `transactions_${this.currentFilter}_${new Date().toISOString().split('T')[0]}.csv`);
            this.showToast('Transactions exported successfully!', 'success');
        }, 1500);
    }
    
    downloadCSV(data, filename) {
        if (data.length === 0) {
            this.showToast('No data to export', 'warning');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    generateReport() {
        this.showToast('Generating financial report...', 'info');
        
        // Simulate report generation
        setTimeout(() => {
            // In a real app, this would redirect to a reports page or generate a PDF
            window.location.href = '/dashboard';
        }, 2000);
    }
    
    initializeModals() {
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.querySelectorAll('input[type="date"]').forEach(input => {
            if (!input.value) {
                input.value = today;
            }
        });
        
        // Clear form when modal is hidden
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('hidden.bs.modal', () => {
                const form = modal.querySelector('form');
                if (form) {
                    form.reset();
                    form.querySelectorAll('.is-invalid').forEach(field => {
                        this.clearFieldError(field);
                    });
                    
                    // Restore button states
                    form.querySelectorAll('button[type="submit"]').forEach(btn => {
                        this.restoreButtonState(btn);
                    });
                }
            });
        });
    }
    
    initializeSearch() {
        // Create search input if it doesn't exist
        const searchContainer = document.querySelector('.recent-transactions .d-flex');
        if (searchContainer && !document.getElementById('transaction-search')) {
            const searchHTML = `
                <div class="me-3">
                    <input type="text" id="transaction-search" class="form-control form-control-sm" 
                           placeholder="Search transactions..." style="width: 200px;">
                </div>
            `;
            searchContainer.insertAdjacentHTML('afterbegin', searchHTML);
            
            // Bind search event
            const searchInput = document.getElementById('transaction-search');
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchTransactions(e.target.value);
                }, 300);
            });
        }
    }
    
    searchTransactions(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            // Show all transactions for current filter
            this.applyFilter(this.currentFilter);
            return;
        }
        
        this.transactions.forEach(transaction => {
            const searchableText = [
                transaction.description,
                transaction.meta,
                transaction.amount.toString(),
                transaction.category
            ].join(' ').toLowerCase();
            
            const matches = searchableText.includes(searchTerm);
            this.animateTransactionVisibility(transaction.element, matches);
        });
        
        this.updateEmptyState();
    }
    
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only trigger if not in an input field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch(e.key) {
                case 'e':
                case 'E':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.showAddExpenseModal();
                    }
                    break;
                case 'i':
                case 'I':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.showAddIncomeModal();
                    }
                    break;
                case 'f':
                case 'F':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        const searchInput = document.getElementById('transaction-search');
                        if (searchInput) {
                            searchInput.focus();
                        }
                    }
                    break;
                case '1':
                    if (!e.ctrlKey && !e.metaKey) {
                        this.triggerFilterTab('all');
                    }
                    break;
                case '2':
                    if (!e.ctrlKey && !e.metaKey) {
                        this.triggerFilterTab('expenses');
                    }
                    break;
                case '3':
                    if (!e.ctrlKey && !e.metaKey) {
                        this.triggerFilterTab('income');
                    }
                    break;
                case '4':
                    if (!e.ctrlKey && !e.metaKey) {
                        this.triggerFilterTab('recent');
                    }
                    break;
            }
        });
    }
    
    triggerFilterTab(filter) {
        const tab = document.querySelector(`[data-filter="${filter}"]`);
        if (tab) {
            tab.click();
        }
    }
    
    startAutoRefresh() {
        // Refresh transaction data every 30 seconds
        setInterval(() => {
            this.refreshTransactionData();
        }, 30000);
    }
    
    refreshTransactionData() {
        if (this.isLoading) return;
        
        // Only refresh if the page is visible
        if (document.hidden) return;
        
        this.isLoading = true;
        
        // Simulate API call to refresh data
        // In a real app, this would fetch updated data from the server
        setTimeout(() => {
            console.log('Transaction data refreshed');
            this.isLoading = false;
        }, 1000);
    }
    
    showToast(message, type = 'success') {
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${this.getToastClass(type)} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Add toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: type === 'error' ? 5000 : 3000
        });
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    getToastClass(type) {
        const classMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classMap[type] || 'success';
    }
    
    getToastIcon(type) {
        const iconMap = {
            'success': 'check',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return iconMap[type] || 'check';
    }
    
    // Public method to add a new transaction to the list
    addTransaction(transactionData) {
        const transactionHTML = this.generateTransactionHTML(transactionData);
        const transactionsList = document.getElementById('transactions-list');
        
        // Remove empty state if it exists
        const emptyState = transactionsList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        // Add new transaction at the top
        transactionsList.insertAdjacentHTML('afterbegin', transactionHTML);
        
        // Reload transactions array
        this.loadTransactions();
        
        // Apply current filter
        this.applyFilter(this.currentFilter);
    }
    
    generateTransactionHTML(data) {
        const isExpense = data.type === 'expense';
        const iconMap = {
            'food': 'fas fa-utensils',
            'transportation': 'fas fa-car',
            'entertainment': 'fas fa-film',
            'other': 'fas fa-ellipsis-h'
        };
        
        const colorMap = {
            'food': '#FF6B6B',
            'transportation': '#4ECDC4',
            'entertainment': '#45B7D1',
            'other': '#96CEB4'
        };
        
        return `
            <div class="transaction-item fade-in" data-type="${data.type}" data-category="${data.category || 'income'}">
                <div class="transaction-icon" style="background-color: ${colorMap[data.category] || '#27ae60'};">
                    <i class="${iconMap[data.category] || 'fas fa-plus'}"></i>
                </div>
                <div class="transaction-details">
                    <div class="transaction-description">${data.description || data.source}</div>
                    <div class="transaction-meta">
                        ${new Date(data.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })} • 
                        ${isExpense ? data.category.charAt(0).toUpperCase() + data.category.slice(1) : 'Income'}
                        ${!isExpense && data.recurrence_period !== 'none' ? ` • ${data.recurrence_period.charAt(0).toUpperCase() + data.recurrence_period.slice(1)}` : ''}
                    </div>
                </div>
                <div class="transaction-amount ${isExpense ? 'amount-expense' : 'amount-income'}">
                    ${isExpense ? '-' : '+'}$${parseFloat(data.amount).toFixed(2)}
                </div>
            </div>
        `;
    }
}

// Global functions for backward compatibility
window.addExpense = function(category) {
    if (window.transactionManager) {
        window.transactionManager.showAddExpenseModal(category);
    }
};

window.exportTransactions = function() {
    if (window.transactionManager) {
        window.transactionManager.exportTransactions();
    }
};

window.generateReport = function() {
    if (window.transactionManager) {
        window.transactionManager.generateReport();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.transactionManager = new TransactionManager();
    
    // Show success messages from server
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get('success');
    const error = urlParams.get('error');
    
    if (success) {
        window.transactionManager.showToast(decodeURIComponent(success), 'success');
    }
    
    if (error) {
        window.transactionManager.showToast(decodeURIComponent(error), 'error');
    }
    
    // Apply initial filter from URL
    const initialFilter = urlParams.get('filter') || 'all';
    if (initialFilter !== 'all') {
        const filterTab = document.querySelector(`[data-filter="${initialFilter}"]`);
        if (filterTab) {
            filterTab.click();
        }
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TransactionManager;
}