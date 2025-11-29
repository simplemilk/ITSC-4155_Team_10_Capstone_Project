const PRIORITY_CATEGORIES = {
    'Save More': {
        icon: '💰',
        description: 'Build your savings and emergency fund',
        color: '#10b981'
    },
    'Reduce Debt': {
        icon: '📉',
        description: 'Pay off loans and credit card balances',
        color: '#ef4444'
    },
    'Invest More': {
        icon: '📈',
        description: 'Grow wealth through investments',
        color: '#3b82f6'
    },
    'Control Spending': {
        icon: '🎯',
        description: 'Manage expenses and stick to budget',
        color: '#f59e0b'
    }
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    renderPriorityCards();
    loadCurrentPriorities();
});

function renderPriorityCards() {
    const container = document.getElementById('priorityCards');
    container.innerHTML = '';
    
    Object.entries(PRIORITY_CATEGORIES).forEach(([name, data]) => {
        const card = document.createElement('div');
        card.className = 'priority-card';
        card.style.setProperty('--priority-color', data.color);
        card.style.setProperty('--priority-color-light', data.color + '20');
        
        card.innerHTML = `
            <div class="priority-icon">${data.icon}</div>
            <h3>${name}</h3>
            <p>${data.description}</p>
        `;
        
        card.onclick = () => openPriorityModal(name);
        container.appendChild(card);
    });
}

function openPriorityModal(priorityName) {
    const modal = document.getElementById('priorityModal');
    const modalTitle = document.getElementById('modalTitle');
    const selectedPriority = document.getElementById('selectedPriority');
    
    modalTitle.textContent = `Set Priority: ${priorityName}`;
    selectedPriority.value = priorityName;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('priorityModal').style.display = 'none';
    document.getElementById('priorityDetailForm').reset();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('priorityModal');
    if (event.target == modal) {
        closeModal();
    }
}

document.querySelector('.close').onclick = closeModal;

// Handle form submission
document.getElementById('priorityDetailForm').onsubmit = async function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        priority: formData.get('priority'),
        importance_level: parseInt(formData.get('importance_level')),
        target_amount: formData.get('target_amount') || null,
        target_date: formData.get('target_date') || null,
        notes: formData.get('notes') || ''
    };
    
    try {
        const response = await fetch('/finance/priorities', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(result.message, 'success');
            closeModal();
            loadCurrentPriorities();
            displaySuggestions(data.priority, result.suggestions);
        } else {
            showNotification(result.error || 'Failed to save priority', 'error');
        }
    } catch (error) {
        showNotification('Error saving priority: ' + error.message, 'error');
    }
};

async function loadCurrentPriorities() {
    try {
        const response = await fetch('/finance/priorities');
        const priorities = await response.json();
        
        if (priorities.length > 0) {
            document.getElementById('currentPriorities').style.display = 'block';
            displayCurrentPriorities(priorities);
        }
    } catch (error) {
        console.error('Error loading priorities:', error);
    }
}

function displayCurrentPriorities(priorities) {
    const container = document.getElementById('activePrioritiesList');
    container.innerHTML = '';
    
    if (priorities.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <h3>No priorities set yet</h3>
                <p>Select a financial priority above to get started</p>
            </div>
        `;
        return;
    }
    
    priorities.forEach(priority => {
        const priorityData = PRIORITY_CATEGORIES[priority.priority_type];
        const item = document.createElement('div');
        item.className = 'active-priority-item';
        item.style.setProperty('--priority-color', priorityData.color);
        
        item.innerHTML = `
            <div class="priority-item-header">
                <div>
                    <span class="priority-icon" style="font-size: 1.5rem;">${priorityData.icon}</span>
                    <span class="priority-item-title">${priority.priority_type}</span>
                    <span class="priority-badge" style="background: ${priorityData.color};">
                        Level ${priority.importance_level}
                    </span>
                </div>
                <div class="priority-actions">
                    <button class="btn-edit" onclick="editPriority(${priority.id})">Edit</button>
                    <button class="btn-delete" onclick="deletePriority(${priority.id})">Delete</button>
                </div>
            </div>
            ${priority.target_amount ? `<p><strong>Target:</strong> $${parseFloat(priority.target_amount).toFixed(2)}</p>` : ''}
            ${priority.target_date ? `<p><strong>By:</strong> ${new Date(priority.target_date).toLocaleDateString()}</p>` : ''}
            ${priority.notes ? `<p><strong>Notes:</strong> ${priority.notes}</p>` : ''}
            <p><small>${priority.actions_count} actions logged</small></p>
        `;
        
        container.appendChild(item);
    });
}

function displaySuggestions(priorityType, suggestions) {
    const section = document.getElementById('suggestionsSection');
    const container = document.getElementById('suggestionsList');
    const priorityData = PRIORITY_CATEGORIES[priorityType];
    
    section.style.display = 'block';
    container.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const card = document.createElement('div');
        card.className = 'suggestion-card';
        card.style.setProperty('--priority-color', priorityData.color);
        
        card.innerHTML = `
            <span class="suggestion-category" style="background: ${priorityData.color};">
                ${suggestion.category || 'General'}
            </span>
            <p class="suggestion-text">${suggestion.text}</p>
            ${suggestion.recommended_amount ? 
                `<p class="suggestion-amount">Recommended: $${suggestion.recommended_amount.toFixed(2)}</p>` : ''}
            <small style="color: #6b7280;">Relevance: ${suggestion.relevance_score}%</small>
        `;
        
        container.appendChild(card);
    });
}

async function deletePriority(priorityId) {
    if (!confirm('Are you sure you want to delete this priority?')) return;
    
    try {
        const response = await fetch(`/finance/priorities/${priorityId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(result.message, 'success');
            loadCurrentPriorities();
        } else {
            showNotification(result.error || 'Failed to delete priority', 'error');
        }
    } catch (error) {
        showNotification('Error deleting priority: ' + error.message, 'error');
    }
}

function editPriority(priorityId) {
    // This would load the priority data and populate the modal
    showNotification('Edit functionality - to be implemented with full priority data fetch', 'info');
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);