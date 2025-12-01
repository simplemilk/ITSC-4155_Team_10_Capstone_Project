/**
 * Investments JavaScript
 */

let currentInvestmentId = null;

/**
 * Edit investment
 */
function editInvestment(id) {
    // TODO: Populate edit form with investment data
    console.log('Edit investment:', id);
    alert('Edit functionality: Populate form with investment data');
}

/**
 * Delete investment
 */
function deleteInvestment(id, assetName) {
    currentInvestmentId = id;
    
    // Set form action
    const form = document.getElementById('deleteInvestmentForm');
    form.action = `/investments/${id}/delete`;
    
    // Set asset name
    document.getElementById('delete-asset-name').textContent = assetName;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('deleteInvestmentModal'));
    modal.show();
}

/**
 * Update price for an investment
 */
function updatePrice(id) {
    const newPrice = prompt('Enter new current price:');
    
    if (newPrice === null) return; // User cancelled
    
    const price = parseFloat(newPrice);
    
    if (isNaN(price) || price < 0) {
        alert('Please enter a valid price (must be 0 or greater)');
        return;
    }
    
    // Send AJAX request
    fetch(`/investments/${id}/update-price`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ current_price: price })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Price updated successfully!');
            location.reload(); // Reload to show updated data
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update price');
    });
}

/**
 * Form validation
 */
document.addEventListener('DOMContentLoaded', function() {
    const addForm = document.getElementById('addInvestmentForm');
    
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            if (!addForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            addForm.classList.add('was-validated');
        });
        
        // Validate purchase date is not in future
        const purchaseDateInput = document.getElementById('purchase_date');
        if (purchaseDateInput) {
            purchaseDateInput.addEventListener('change', function() {
                const selectedDate = new Date(this.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (selectedDate > today) {
                    this.setCustomValidity('Purchase date cannot be in the future');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
        
        // Validate numeric inputs
        const numericInputs = ['quantity', 'purchase_price', 'current_price'];
        numericInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', function() {
                    const value = parseFloat(this.value);
                    const min = parseFloat(this.min);
                    
                    if (isNaN(value) || (min && value < min)) {
                        this.setCustomValidity(`Value must be ${min || 0} or greater`);
                    } else {
                        this.setCustomValidity('');
                    }
                });
            }
        });
    }
});