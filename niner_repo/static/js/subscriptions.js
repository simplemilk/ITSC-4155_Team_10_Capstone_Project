/**
 * Subscriptions JavaScript
 */

let currentSubscriptionId = null;

/**
 * Show cancel subscription confirmation modal
 */
function showCancelModal(id, name, amount) {
    currentSubscriptionId = id;
    
    // Set form action
    const form = document.getElementById('cancelSubscriptionForm');
    form.action = `/subscriptions/${id}/cancel`;
    
    // Populate details
    document.getElementById('cancel-sub-name').textContent = name;
    document.getElementById('cancel-sub-amount').textContent = amount.toFixed(2);
    
    // Reset checkbox
    document.getElementById('confirmCancel').checked = false;
    document.getElementById('confirmCancelBtn').disabled = true;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('cancelSubscriptionModal'));
    modal.show();
}

/**
 * Edit subscription (placeholder for future implementation)
 */
function editSubscription(id) {
    // TODO: Implement edit modal
    console.log('Edit subscription:', id);
    alert('Edit functionality coming soon!');
}

/**
 * Enable/disable cancel button based on confirmation checkbox
 */
document.addEventListener('DOMContentLoaded', function() {
    // Set default next billing date to next month
    const nextBillingInput = document.getElementById('next_billing_date');
    if (nextBillingInput) {
        const nextMonth = new Date();
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        nextBillingInput.value = nextMonth.toISOString().split('T')[0];
    }
    
    // Handle cancel confirmation checkbox
    const confirmCheckbox = document.getElementById('confirmCancel');
    const confirmBtn = document.getElementById('confirmCancelBtn');
    
    if (confirmCheckbox && confirmBtn) {
        confirmCheckbox.addEventListener('change', function() {
            confirmBtn.disabled = !this.checked;
        });
    }
    
    // Handle cancel form submission
    const cancelForm = document.getElementById('cancelSubscriptionForm');
    if (cancelForm) {
        cancelForm.addEventListener('submit', function(e) {
            if (!confirmCheckbox.checked) {
                e.preventDefault();
                alert('Please confirm that you want to cancel this subscription.');
                return false;
            }
        });
    }
});