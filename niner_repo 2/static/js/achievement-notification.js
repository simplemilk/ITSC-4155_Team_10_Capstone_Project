/**
 * Achievement Notification System
 * Handles display of achievement, badge, and level-up notifications
 */

// Initialize achievement notifications when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeAchievementNotifications();
});

function initializeAchievementNotifications() {
    // Get achievement notifications from data attribute
    const container = document.getElementById('achievementToastContainer');
    if (!container) return;
    
    const notificationsData = container.getAttribute('data-notifications');
    if (!notificationsData) return;
    
    try {
        const achievementNotifications = JSON.parse(notificationsData);
        
        if (achievementNotifications.length > 0) {
            setTimeout(() => {
                achievementNotifications.forEach((notification, index) => {
                    setTimeout(() => {
                        showAchievementToast(notification.category, notification.data);
                    }, index * 500); // Stagger notifications
                });
            }, 500); // Delay initial show
        }
    } catch (error) {
        console.error('Error parsing achievement notifications:', error);
    }
}

function showAchievementToast(type, data) {
    const container = document.getElementById('achievementToastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    
    let toastClass = 'achievement-toast';
    let headerTitle = '';
    let content = '';
    
    if (type === 'achievement') {
        headerTitle = `<i class="fas fa-trophy"></i> Achievement Unlocked!`;
        content = `
            <div class="achievement-icon-large">
                <i class="fas ${data.icon}"></i>
            </div>
            <div class="achievement-content">
                <div class="achievement-name">${escapeHtml(data.name)}</div>
                <div class="achievement-description">${escapeHtml(data.description)}</div>
                <span class="achievement-points">
                    <i class="fas fa-coins"></i> +${data.points} points
                </span>
                <span class="achievement-tier tier-${data.tier}">${data.tier}</span>
            </div>
        `;
        playAchievementSound();
        launchConfetti();
    } else if (type === 'badge') {
        toastClass += ' badge-toast';
        headerTitle = `<i class="fas fa-certificate"></i> Badge Earned!`;
        content = `
            <div class="achievement-icon-large">
                <i class="fas ${data.icon}"></i>
            </div>
            <div class="achievement-content">
                <div class="achievement-name">${escapeHtml(data.name)}</div>
                <div class="achievement-description">${escapeHtml(data.description)}</div>
                <span class="achievement-tier rarity-${data.rarity}">${data.rarity}</span>
            </div>
        `;
        playBadgeSound();
        launchConfetti();
    } else if (type === 'level_up') {
        toastClass += ' level-up-toast';
        headerTitle = `<i class="fas fa-star"></i> Level Up!`;
        content = `
            <div class="text-center">
                <div class="level-badge-large position-relative">
                    <i class="fas ${data.icon}"></i>
                    <div class="level-number-badge">${data.level}</div>
                </div>
                <div class="achievement-name">${escapeHtml(data.level_name)}</div>
                <div class="achievement-description">
                    Points Multiplier: ${data.multiplier}x
                </div>
            </div>
        `;
        playLevelUpSound();
        launchConfetti(true); // Extra confetti for level up
    }
    
    toast.className = toastClass;
    toast.innerHTML = `
        <div class="achievement-toast-header">
            <div class="achievement-toast-title">${headerTitle}</div>
            <button class="toast-close-btn" onclick="closeAchievementToast(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="achievement-toast-body">
            ${content}
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        closeAchievementToast(toast.querySelector('.toast-close-btn'));
    }, 5000);
}

function closeAchievementToast(btn) {
    if (!btn) return;
    const toast = btn.closest('.achievement-toast');
    if (!toast) return;
    
    toast.classList.add('hiding');
    setTimeout(() => {
        toast.remove();
    }, 500);
}

function playAchievementSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAo=');
        audio.volume = 0.3;
        audio.play().catch(() => {});
    } catch (error) {
        console.log('Achievement sound not available');
    }
}

function playBadgeSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAo=');
        audio.volume = 0.4;
        audio.play().catch(() => {});
    } catch (error) {
        console.log('Badge sound not available');
    }
}

function playLevelUpSound() {
    try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAo=');
        audio.volume = 0.5;
        audio.play().catch(() => {});
    } catch (error) {
        console.log('Level up sound not available');
    }
}

function launchConfetti(intense = false) {
    const count = intense ? 100 : 50;
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#FFD700', '#f5576c'];
    
    for (let i = 0; i < count; i++) {
        setTimeout(() => {
            createConfettiParticle(colors[Math.floor(Math.random() * colors.length)]);
        }, i * 20);
    }
}

function createConfettiParticle(color) {
    const particle = document.createElement('div');
    particle.className = 'confetti-particle';
    particle.style.backgroundColor = color;
    particle.style.left = Math.random() * window.innerWidth + 'px';
    particle.style.top = '-10px';
    
    document.body.appendChild(particle);
    
    const animation = particle.animate([
        { 
            transform: 'translateY(0) rotate(0deg)',
            opacity: 1
        },
        { 
            transform: `translateY(${window.innerHeight + 50}px) rotate(${Math.random() * 720}deg)`,
            opacity: 0
        }
    ], {
        duration: 2000 + Math.random() * 2000,
        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });
    
    animation.onfinish = () => particle.remove();
}

// Utility function to escape HTML
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

// Make closeAchievementToast available globally for onclick handlers
window.closeAchievementToast = closeAchievementToast;