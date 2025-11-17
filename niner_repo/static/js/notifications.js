/**
 * Notification Center JavaScript
 * Handles notification interactions, filtering, and real-time updates
 */

// State management
let currentFilter = 'all';
let notifications = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNotifications();
    setupEventListeners();
    startPolling();
});

/**
 * Initialize notification system
 */
function initializeNotifications() {
    loadNotifications();
    updateUnreadCount();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Mark all as read button
    const markAllReadBtn = document.getElementById('markAllRead');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllAsRead);
    }

    // Clear all button
    const clearAllBtn = document.getElementById('clearAll');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllNotifications);
    }

    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            filterNotifications();
        });
    });

    // Mark individual notification as read
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('mark-read')) {
            const notificationId = e.target.dataset.id;
            markAsRead(notificationId);
        }
    });

    // Delete individual notification
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-notification')) {
            const notificationId = e.target.dataset.id;
            deleteNotification(notificationId);
        }
    });
}

/**
 * Load notifications from API
 */
async function loadNotifications() {
    try {
        const response = await fetch('/notifications/api/list');
        const data = await response.json();
        
        if (data.success) {
            notifications = data.notifications;
            renderNotifications(notifications);
            updateUnreadCount(data.unread_count);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

/**
 * Render notifications to the page
 */
function renderNotifications(notificationsToRender) {
    const listContainer = document.getElementById('notificationsList');
    if (!listContainer) return;

    if (notificationsToRender.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔔</div>
                <h3>No notifications</h3>
                <p>${currentFilter === 'unread' ? 'No unread notifications' : "You're all caught up!"}</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = notificationsToRender.map(notification => `
        <div class="notification-card ${notification.severity} ${notification.is_read ? 'read' : 'unread'}" 
             data-id="${notification.id}"
             data-type="${notification.type}">
            <div class="notification-content">
                <div class="notification-title">
                    ${notification.title}
                    ${!notification.is_read ? '<span class="unread-badge">New</span>' : ''}
                </div>
                <div class="notification-message">${notification.message}</div>
                <div class="notification-meta">
                    <span class="notification-time">${formatDate(notification.created_at)}</span>
                    ${notification.metadata && notification.metadata.category ? 
                        `<span class="notification-category">${notification.metadata.category}</span>` : ''}
                </div>
            </div>
            <div class="notification-actions-inline">
                ${!notification.is_read ? `
                    <button class="btn-icon mark-read" data-id="${notification.id}" title="Mark as read">
                        ✓
                    </button>
                ` : ''}
                <button class="btn-icon delete-notification" data-id="${notification.id}" title="Delete">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Filter notifications based on current filter
 */
function filterNotifications() {
    let filtered = notifications;

    if (currentFilter === 'unread') {
        filtered = notifications.filter(n => !n.is_read);
    } else if (currentFilter !== 'all') {
        filtered = notifications.filter(n => n.type === currentFilter);
    }

    renderNotifications(filtered);
}

/**
 * Mark a notification as read
 */
async function markAsRead(notificationId) {
    try {
        const response = await fetch(`/notifications/api/mark-read/${notificationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            // Update local state
            const notification = notifications.find(n => n.id == notificationId);
            if (notification) {
                notification.is_read = true;
            }
            
            // Re-render
            filterNotifications();
            updateUnreadCount();
            
            // Show success message
            showToast('Marked as read', 'success');
        }
    } catch (error) {
        console.error('Error marking as read:', error);
        showToast('Error marking notification as read', 'error');
    }
}

/**
 * Mark all notifications as read
 */
async function markAllAsRead() {
    if (!confirm('Mark all notifications as read?')) return;

    try {
        const response = await fetch('/notifications/api/mark-all-read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            // Update local state
            notifications.forEach(n => n.is_read = true);
            
            // Re-render
            filterNotifications();
            updateUnreadCount();
            
            showToast('All notifications marked as read', 'success');
        }
    } catch (error) {
        console.error('Error marking all as read:', error);
        showToast('Error marking all as read', 'error');
    }
}

/**
 * Delete a notification
 */
async function deleteNotification(notificationId) {
    try {
        const response = await fetch(`/notifications/api/delete/${notificationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            // Remove from local state
            notifications = notifications.filter(n => n.id != notificationId);
            
            // Re-render
            filterNotifications();
            updateUnreadCount();
            
            showToast('Notification deleted', 'success');
        }
    } catch (error) {
        console.error('Error deleting notification:', error);
        showToast('Error deleting notification', 'error');
    }
}

/**
 * Clear all notifications
 */
async function clearAllNotifications() {
    if (!confirm('Delete all notifications? This cannot be undone.')) return;

    try {
        const response = await fetch('/notifications/api/clear-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            notifications = [];
            filterNotifications();
            updateUnreadCount();
            showToast('All notifications cleared', 'success');
        }
    } catch (error) {
        console.error('Error clearing notifications:', error);
        showToast('Error clearing notifications', 'error');
    }
}

/**
 * Update unread count display
 */
async function updateUnreadCount(count) {
    if (count === undefined) {
        try {
            const response = await fetch('/notifications/api/unread-count');
            const data = await response.json();
            if (data.success) {
                count = data.count;
            }
        } catch (error) {
            console.error('Error fetching unread count:', error);
            return;
        }
    }

    const unreadCountElement = document.getElementById('unreadCount');
    if (unreadCountElement) {
        unreadCountElement.textContent = count;
    }

    // Update navbar badge if it exists
    updateNavbarBadge(count);
}

/**
 * Update notification badge in navbar
 */
function updateNavbarBadge(count) {
    let badge = document.querySelector('.notification-badge');
    
    if (count > 0) {
        if (!badge) {
            const notifLink = document.querySelector('a[href*="notifications"]');
            if (notifLink) {
                badge = document.createElement('span');
                badge.className = 'notification-badge';
                notifLink.style.position = 'relative';
                notifLink.appendChild(badge);
            }
        }
        if (badge) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
        }
    } else if (badge) {
        badge.style.display = 'none';
    }
}

/**
 * Start polling for new notifications
 */
function startPolling() {
    // Poll every 30 seconds
    setInterval(() => {
        loadNotifications();
    }, 30000);
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${type === 'success' ? '#00703C' : '#dc3545'};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations
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

    .notification-badge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #dc3545;
        color: white;
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: bold;
        min-width: 18px;
        text-align: center;
    }
`;
document.head.appendChild(style);
