/**
 * Transaction Page JavaScript
 * Handles filtering, interactions, and dynamic content for the transaction page
 */

class TransactionManager {
    constructor() {
        this.transactions = [];
        this.filteredTransactions = [];
        this.currentFilter = 'all';
        this.currentTimeFilter = 'all';
        this.isLoading = false;
        this.isDeletedView = false;
        
        this.init();
    }
    
    init() {
        this.loadTransactions();
        this.bindEvents();
        this.initializeModals();
        this.showFlashMessages();
        this.initializeDeletedView();
    }
    
    initializeDeletedView() {
        // Toggle between active and deleted transactions
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const filter = tab.dataset.filter;
                
                if (filter === 'deleted') {
                    this.showDeletedView();
                } else if (filter === 'recent') {
                    this.handleTimeFilterChange(filter);
                } else {
                    this.showActiveView();
                    if (filter !== 'deleted') {
                        this.handleFilterChange(filter);
                    }
                }
            });
        });
    }
    
    showDeletedView() {
        this.isDeletedView = true;
        
        // Toggle visibility
        const transactionsList = document.getElementById('transactions-list');
        const deletedList = document.getElementById('deleted-transactions-list');
        const deletedAlert = document.getElementById('deleted-alert');
        const statsSection = document.getElementById('stats-section');
        const categorySection = document.getElementById('category-section');
        const quickActionsSection = document.getElementById('quick-actions-section');
        const headerTitle = document.getElementById('header-title');
        const headerSubtitle = document.getElementById('header-subtitle');
        const headerActions = document.getElementById('header-actions');
        const transactionsTitle = document.getElementById('transactions-title');
        const transactionCount = document.getElementById('transaction-count');
        
        if (transactionsList) transactionsList.style.display = 'none';
        if (deletedList) deletedList.style.display = 'block';
        if (deletedAlert) deletedAlert.style.display = 'block';
        if (statsSection) statsSection.style.display = 'none';
        if (categorySection) categorySection.style.display = 'none';
        if (quickActionsSection) quickActionsSection.style.display = 'none';
        if (headerTitle) headerTitle.textContent = 'Deleted Transactions';
        if (headerSubtitle) headerSubtitle.textContent = 'Restore or permanently delete transactions';
        if (headerActions) headerActions.style.display = 'none';
        if (transactionsTitle) transactionsTitle.innerHTML = '<i class="fas fa-trash-restore me-2"></i>Deleted Transactions';
        
        // Update count
        const deletedItems = document.querySelectorAll('#deleted-transactions-list .transaction-item');
        if (transactionCount) transactionCount.textContent = deletedItems.length;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(tab => {
            if (tab.dataset.filter === 'deleted') {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
    }
    
    showActiveView() {
        this.isDeletedView = false;
        
        // Toggle visibility
        const transactionsList = document.getElementById('transactions-list');
        const deletedList = document.getElementById('deleted-transactions-list');
        const deletedAlert = document.getElementById('deleted-alert');
        const statsSection = document.getElementById('stats-section');
        const categorySection = document.getElementById('category-section');
        const quickActionsSection = document.getElementById('quick-actions-section');
        const headerTitle = document.getElementById('header-title');
        const headerSubtitle = document.getElementById('header-subtitle');
        const headerActions = document.getElementById('header-actions');
        const transactionsTitle = document.getElementById('transactions-title');
        const transactionCount = document.getElementById('transaction-count');
        
        if (transactionsList) transactionsList.style.display = 'block';
        if (deletedList) deletedList.style.display = 'none';
        if (deletedAlert) deletedAlert.style.display = 'none';
        if (statsSection) statsSection.style.display = 'flex';
        if (categorySection) categorySection.style.display = 'flex';
        if (quickActionsSection) quickActionsSection.style.display = 'flex';
        if (headerTitle) headerTitle.textContent = 'Transaction Management';
        if (headerSubtitle) headerSubtitle.textContent = 'Track your income and expenses in one place';
        if (headerActions) headerActions.style.display = 'block';
        if (transactionsTitle) transactionsTitle.innerHTML = '<i class="fas fa-history me-2"></i>Recent Transactions';
        
        // Update count
        const activeItems = document.querySelectorAll('#transactions-list .transaction-item');
        if (transactionCount) transactionCount.textContent = activeItems.length;
    }
    
    bindEvents() {
        // Filter tab events handled in initializeDeletedView
        
        // Quick add expense buttons (in category cards)
        document.querySelectorAll('[data-category]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const category = btn.dataset.category;
                this.showAddExpenseModal(category);
            });
        });
        
        // Prevent clicks on transaction items but allow delete button
        this.preventTransactionClicks();
    }
    
    preventTransactionClicks() {
        document.querySelectorAll('.transaction-item:not([data-deleted])').forEach(item => {
            // Make the item itself non-clickable
            item.style.cursor = 'default';
            
            // Disable pointer events on non-interactive elements
            const icon = item.querySelector('.transaction-icon');
            const details = item.querySelector('.transaction-details');
            const amount = item.querySelector('.transaction-amount');
            
            if (icon) icon.style.pointerEvents = 'none';
            if (details) details.style.pointerEvents = 'none';
            if (amount) amount.style.pointerEvents = 'none';
            
            // Ensure delete button works by re-attaching the event listener
            const deleteBtn = item.querySelector('.transaction-actions .btn-outline-danger');
            if (deleteBtn) {
                // Get transaction info
                const transactionId = item.dataset.id;
                const description = item.querySelector('.transaction-description')?.textContent.trim() || '';
                
                // Remove onclick attribute and use event listener instead
                deleteBtn.removeAttribute('onclick');
                
                // Clone to remove old listeners
                const newBtn = deleteBtn.cloneNode(true);
                deleteBtn.parentNode.replaceChild(newBtn, deleteBtn);
                
                // Add new event listener
                newBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    deleteTransaction(transactionId, description);
                });
                
                // Ensure button is fully interactive
                newBtn.style.pointerEvents = 'auto';
                newBtn.style.cursor = 'pointer';
                newBtn.style.zIndex = '10000';
            }
        });
    }
    
    loadTransactions() {
        const transactionItems = document.querySelectorAll('#transactions-list .transaction-item');
        this.transactions = Array.from(transactionItems).map(item => {
            const dateAttr = item.dataset.date;
            let transactionDate = new Date();
            
            if (dateAttr) {
                if (dateAttr.match(/^\d{4}-\d{2}-\d{2}$/)) {
                    transactionDate = new Date(dateAttr + 'T00:00:00');
                } else {
                    transactionDate = new Date(dateAttr);
                }
            } else {
                const metaText = item.querySelector('.transaction-meta')?.textContent || '';
                const dateMatch = metaText.match(/(\d{4}-\d{2}-\d{2})/);
                if (dateMatch) {
                    transactionDate = new Date(dateMatch[1] + 'T00:00:00');
                }
            }
            
            return {
                element: item,
                type: item.dataset.type || 'expense',
                category: item.dataset.category || 'other',
                description: item.querySelector('.transaction-description')?.textContent.trim() || '',
                amount: parseFloat(item.querySelector('.transaction-amount')?.textContent.replace(/[^0-9.-]/g, '') || 0),
                date: transactionDate,
                dateStr: transactionDate.toISOString().split('T')[0],
                meta: item.querySelector('.transaction-meta')?.textContent || ''
            };
        });
        
        this.filteredTransactions = [...this.transactions];
        console.log('Loaded transactions:', this.transactions.length);
    }
    
    handleFilterChange(filter) {
        console.log('Category filter changed to:', filter);
        
        document.querySelectorAll('.filter-tab').forEach(tab => {
            if (tab.dataset.filter !== 'recent' && tab.dataset.filter !== 'deleted') {
                if (tab.dataset.filter === filter) {
                    tab.classList.add('active');
                } else {
                    tab.classList.remove('active');
                }
            }
        });
        
        this.currentFilter = filter;
        this.applyFilters();
    }
    
    handleTimeFilterChange(timeFilter) {
        console.log('Time filter changed to:', timeFilter);
        
        const recentTab = document.querySelector('.filter-tab[data-filter="recent"]');
        if (recentTab) {
            if (this.currentTimeFilter === 'recent') {
                this.currentTimeFilter = 'all';
                recentTab.classList.remove('active');
            } else {
                this.currentTimeFilter = 'recent';
                recentTab.classList.add('active');
            }
        }
        
        this.applyFilters();
    }
    
    applyFilters() {
        const now = new Date();
        now.setHours(23, 59, 59, 999);
        
        const sevenDaysAgo = new Date(now);
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        sevenDaysAgo.setHours(0, 0, 0, 0);
        
        console.log('Applying filters - Category:', this.currentFilter, 'Time:', this.currentTimeFilter);
        
        let visibleCount = 0;
        
        this.transactions.forEach(transaction => {
            let showCategory = false;
            let showTime = false;
            
            switch(this.currentFilter) {
                case 'all':
                    showCategory = true;
                    break;
                case 'expenses':
                    showCategory = transaction.type === 'expense';
                    break;
                case 'income':
                    showCategory = transaction.type === 'income';
                    break;
                case 'food':
                case 'transportation':
                case 'entertainment':
                case 'other':
                    showCategory = transaction.category === this.currentFilter;
                    break;
                default:
                    showCategory = transaction.category === this.currentFilter;
            }
            
            if (this.currentTimeFilter === 'recent') {
                const transDate = new Date(transaction.date);
                transDate.setHours(0, 0, 0, 0);
                showTime = transDate >= sevenDaysAgo && transDate <= now;
            } else {
                showTime = true;
            }
            
            const show = showCategory && showTime;
            
            if (show) {
                visibleCount++;
                transaction.element.classList.remove('filtering-out');
                transaction.element.style.display = 'flex';
                void transaction.element.offsetWidth;
                transaction.element.classList.add('fade-in');
                
                setTimeout(() => {
                    transaction.element.classList.remove('fade-in');
                }, 300);
            } else {
                transaction.element.classList.add('filtering-out');
                transaction.element.classList.remove('fade-in');
                
                setTimeout(() => {
                    if (transaction.element.classList.contains('filtering-out')) {
                        transaction.element.style.display = 'none';
                    }
                }, 300);
            }
        });
        
        console.log(`Filters applied - Showing ${visibleCount} of ${this.transactions.length} transactions`);
        
        setTimeout(() => {
            this.filteredTransactions = this.transactions.filter(t => 
                t.element.style.display !== 'none'
            );
            this.updateEmptyState();
            this.preventTransactionClicks();
        }, 350);
        
        this.updateURL();
    }
    
    updateEmptyState() {
        const transactionsContainer = document.querySelector('#transactions-list');
        if (!transactionsContainer) return;
        
        const originalEmptyState = transactionsContainer.querySelector('.empty-state:not(.filter-empty-state)');
        
        if (this.transactions.length === 0) {
            if (originalEmptyState) {
                originalEmptyState.style.display = 'block';
            }
            return;
        } else {
            if (originalEmptyState) {
                originalEmptyState.style.display = 'none';
            }
        }
        
        let filterEmptyState = transactionsContainer.querySelector('.filter-empty-state');
        
        if (this.filteredTransactions.length === 0) {
            if (!filterEmptyState) {
                filterEmptyState = document.createElement('div');
                filterEmptyState.className = 'empty-state filter-empty-state';
                filterEmptyState.innerHTML = `
                    <div class="empty-state-icon">
                        <i class="fas fa-filter"></i>
                    </div>
                    <h4>No transactions match your filters</h4>
                    <p class="text-muted">
                        ${this.getFilterDisplayText()}
                    </p>
                    <button class="btn btn-outline-primary" onclick="window.transactionManager.clearAllFilters()">
                        <i class="fas fa-times me-2"></i>Clear Filters
                    </button>
                `;
                transactionsContainer.appendChild(filterEmptyState);
            }
            filterEmptyState.style.display = 'block';
        } else {
            if (filterEmptyState) {
                filterEmptyState.style.display = 'none';
            }
        }
    }
    
    getFilterDisplayText() {
        let message = '';
        
        if (this.currentFilter === 'all') {
            message = 'No transactions';
        } else if (this.currentFilter === 'expenses') {
            message = 'No expense transactions';
        } else if (this.currentFilter === 'income') {
            message = 'No income transactions';
        } else {
            message = `No ${this.currentFilter} transactions`;
        }
        
        if (this.currentTimeFilter === 'recent') {
            message += ' in the last 7 days';
        }
        
        return message + '. Try adjusting your filters.';
    }
    
    clearAllFilters() {
        this.currentFilter = 'all';
        this.currentTimeFilter = 'all';
        
        document.querySelectorAll('.filter-tab').forEach(tab => {
            if (tab.dataset.filter === 'all') {
                tab.classList.add('active');
            } else if (tab.dataset.filter !== 'deleted') {
                tab.classList.remove('active');
            }
        });
        
        this.applyFilters();
        this.showToast('Filters cleared', 'success');
    }
    
    updateURL() {
        if (window.history && window.history.pushState) {
            const url = new URL(window.location);
            
            if (this.currentFilter !== 'all') {
                url.searchParams.set('filter', this.currentFilter);
            } else {
                url.searchParams.delete('filter');
            }
            
            if (this.currentTimeFilter === 'recent') {
                url.searchParams.set('timeFilter', 'recent');
            } else {
                url.searchParams.delete('timeFilter');
            }
            
            window.history.pushState({
                filter: this.currentFilter,
                timeFilter: this.currentTimeFilter
            }, '', url);
        }
    }
    
    showAddExpenseModal(category = '') {
        const modal = document.getElementById('addExpenseModal');
        if (modal) {
            const categorySelect = modal.querySelector('#expense-category');
            if (categorySelect && category) {
                categorySelect.value = category;
            }
            
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
            document.body.classList.remove('modal-open');
            
            const bsModal = new bootstrap.Modal(modal, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
            bsModal.show();
        }
    }
    
    showAddIncomeModal() {
        const modal = document.getElementById('addIncomeModal');
        if (modal) {
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
            document.body.classList.remove('modal-open');
            
            const bsModal = new bootstrap.Modal(modal, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
            bsModal.show();
        }
    }
    
    initializeModals() {
        const today = new Date().toISOString().split('T')[0];
        const expenseDate = document.getElementById('expense-date');
        const incomeDate = document.getElementById('income-date');
        
        if (expenseDate) expenseDate.value = today;
        if (incomeDate) incomeDate.value = today;
        
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('hidden.bs.modal', function () {
                document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                    backdrop.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            });
        });
    }
    
    showFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(msg => {
            const message = msg.textContent;
            this.showToast(message, 'success');
        });
        
        const urlParams = new URLSearchParams(window.location.search);
        const success = urlParams.get('success');
        const error = urlParams.get('error');
        
        if (success) {
            this.showToast(decodeURIComponent(success), 'success');
        }
        if (error) {
            this.showToast(decodeURIComponent(error), 'error');
        }
        
        let initialFilter = urlParams.get('filter') || urlParams.get('category') || 'all';
        let initialTimeFilter = urlParams.get('timeFilter') || 'all';
        
        const categoryMap = {
            'food': 'food',
            'transportation': 'transportation',
            'entertainment': 'entertainment',
            'other': 'other'
        };
        
        if (categoryMap[initialFilter]) {
            initialFilter = categoryMap[initialFilter];
        }
        
        setTimeout(() => {
            if (initialFilter && initialFilter !== 'all') {
                this.handleFilterChange(initialFilter);
            }
            if (initialTimeFilter === 'recent') {
                this.handleTimeFilterChange('recent');
            }
        }, 100);
    }
    
    showToast(message, type = 'success') {
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '99999';
            document.body.appendChild(toastContainer);
        }
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, {delay: 3000});
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
    
    exportTransactions() {
        const csvData = this.generateCSV();
        this.downloadCSV(csvData, `transactions-${new Date().toISOString().split('T')[0]}.csv`);
        this.showToast('Transactions exported successfully!', 'success');
    }
    
    generateCSV() {
        const headers = ['Date', 'Description', 'Category', 'Type', 'Amount'];
        const rows = this.filteredTransactions.map(t => [
            t.date.toLocaleDateString(),
            t.description,
            t.category,
            t.type,
            t.amount.toFixed(2)
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
    
    downloadCSV(content, filename) {
        const blob = new Blob([content], { type: 'text/csv' });
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
        this.showToast('Report generation feature coming soon!', 'info');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.transactionManager = new TransactionManager();
});

// Global functions
window.addExpense = function(category) {
    if (window.transactionManager) {
        window.transactionManager.showAddExpenseModal(category);
    }
};

window.addIncome = function() {
    if (window.transactionManager) {
        window.transactionManager.showAddIncomeModal();
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

function setExpenseCategory(category) {
    const categorySelect = document.getElementById('expense-category');
    if (categorySelect) {
        categorySelect.value = category;
    }
}

function deleteTransaction(id, description) {
    const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    document.getElementById('deleteTransactionName').textContent = description;
    document.getElementById('deleteForm').action = `/transactions/${id}/delete`;
    modal.show();
}

// Functions for permanent delete (deleted transactions view)
function confirmPermanentDelete(id, description) {
    const modal = new bootstrap.Modal(document.getElementById('permanentDeleteModal'));
    document.getElementById('permanentDeleteName').textContent = description;
    document.getElementById('permanentDeleteForm').action = `/transactions/${id}/permanent-delete`;
    modal.show();
}

function confirmPermanentDeleteAll() {
    if (confirm('⚠️ WARNING: This will permanently delete ALL deleted transactions. This action cannot be undone!\n\nAre you sure you want to continue?')) {
        // This URL needs to be defined in your Flask routes
        window.location.href = '/transactions/permanent-delete-all';
    }
}