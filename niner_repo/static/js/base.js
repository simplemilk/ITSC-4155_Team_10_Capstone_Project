/**
 * Notification System
 * Handles notification badge updates and dropdown content
 */

// Poll for new notifications every 30 seconds
function updateNotifications() {
    fetch('/notifications/api/unread-count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notificationBadge');
            if (badge && data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'inline';
            } else if (badge) {
                badge.style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Load recent notifications for dropdown
function loadRecentNotifications() {
    fetch('/notifications/api/recent')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('notificationsList');
            if (!list) return;
            
            if (data.notifications && data.notifications.length > 0) {
                list.innerHTML = data.notifications.map(n => createNotificationItem(n)).join('');
            } else {
                list.innerHTML = createEmptyNotificationMessage();
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
            const list = document.getElementById('notificationsList');
            if (list) {
                list.innerHTML = createErrorMessage();
            }
        });
}

// Create notification item HTML
function createNotificationItem(notification) {
    const isUnread = !notification.is_read;
    const severityIcon = getSeverityIcon(notification.severity);
    const severityClass = getSeverityClass(notification.severity);
    const messagePreview = truncateMessage(notification.message, 50);
    const formattedDate = formatNotificationDate(notification.created_at);
    
    return `
        <li>
            <a class="dropdown-item py-2 ${isUnread ? 'bg-light' : ''}" href="/notifications/${notification.id}">
                <div class="d-flex align-items-start">
                    <i class="fas fa-${severityIcon} ${severityClass} me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <div class="fw-bold small">${escapeHtml(notification.title)}</div>
                        <div class="text-muted small">${escapeHtml(messagePreview)}</div>
                        <div class="text-muted small">${formattedDate}</div>
                    </div>
                </div>
            </a>
        </li>
    `;
}

// Get severity icon
function getSeverityIcon(severity) {
    const icons = {
        'critical': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[severity] || 'info-circle';
}

// Get severity CSS class
function getSeverityClass(severity) {
    const classes = {
        'critical': 'text-danger',
        'warning': 'text-warning',
        'info': 'text-info'
    };
    return classes[severity] || 'text-info';
}

// Truncate message
function truncateMessage(message, maxLength) {
    if (message.length <= maxLength) {
        return message;
    }
    return message.substring(0, maxLength) + '...';
}

// Format notification date
function formatNotificationDate(dateString) {
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    } catch (error) {
        return 'Recently';
    }
}

// Create empty notification message
function createEmptyNotificationMessage() {
    return `
        <div class="text-center py-3 text-muted">
            <i class="fas fa-bell-slash fa-2x mb-2"></i>
            <p class="mb-0">No notifications</p>
        </div>
    `;
}

// Create error message
function createErrorMessage() {
    return `
        <div class="text-center py-3 text-danger">
            <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
            <p class="mb-0">Error loading notifications</p>
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Initialize notifications on page load
document.addEventListener('DOMContentLoaded', function() {
    // Only run if user is logged in (check if notification elements exist)
    const notificationBadge = document.getElementById('notificationBadge');
    if (!notificationBadge) {
        return; // User not logged in
    }
    
    // Initial update
    updateNotifications();
    
    // Poll every 30 seconds
    setInterval(updateNotifications, 30000);
    
    // Load notifications when dropdown is clicked
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    if (notificationsDropdown) {
        notificationsDropdown.addEventListener('click', function(e) {
            // Prevent dropdown from closing when clicking inside
            e.stopPropagation();
            loadRecentNotifications();
        });
        
        // Also load on dropdown show event
        const dropdownElement = document.querySelector('#notificationsDropdown');
        if (dropdownElement) {
            dropdownElement.addEventListener('show.bs.dropdown', function() {
                loadRecentNotifications();
            });
        }
    }
});

// Export functions for use in other scripts if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        updateNotifications,
        loadRecentNotifications
    };
}