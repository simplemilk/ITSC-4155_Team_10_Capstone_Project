/**
 * Gamification JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeGamification();
});

function initializeGamification() {
    // Animate numbers on load
    animateCounters();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Confetti for achievements
    checkForNewAchievements();
    
    // Progress bar animations
    animateProgressBars();
}

/**
 * Animate counter numbers
 */
function animateCounters() {
    const counters = document.querySelectorAll('.stat-item strong');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, ''));
        if (isNaN(target)) return;
        
        const duration = 1000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target.toLocaleString();
            }
        };
        
        updateCounter();
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Check for new achievements and show celebration
 */
function checkForNewAchievements() {
    // Check if there's a new achievement in the flash messages
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        if (message.textContent.includes('Achievement Unlocked') || 
            message.textContent.includes('Level Up')) {
            showCelebration();
        }
    });
}

/**
 * Show celebration animation
 */
function showCelebration() {
    // Create confetti effect (simple version)
    const confettiCount = 50;
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            createConfetti(colors[Math.floor(Math.random() * colors.length)]);
        }, i * 30);
    }
    
    // Play sound if available
    playAchievementSound();
}

/**
 * Create a confetti particle
 */
function createConfetti(color) {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = color;
    confetti.style.left = Math.random() * window.innerWidth + 'px';
    confetti.style.top = '-10px';
    confetti.style.opacity = '1';
    confetti.style.zIndex = '9999';
    confetti.style.borderRadius = '50%';
    confetti.style.pointerEvents = 'none';
    
    document.body.appendChild(confetti);
    
    const animation = confetti.animate([
        { 
            transform: 'translateY(0) rotate(0deg)',
            opacity: 1
        },
        { 
            transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`,
            opacity: 0
        }
    ], {
        duration: 3000 + Math.random() * 2000,
        easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    });
    
    animation.onfinish = () => confetti.remove();
}

/**
 * Play achievement sound
 */
function playAchievementSound() {
    // Only play if user has interacted with the page
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjiR1/LMeSwFJHfH8N2QQAo=');
    audio.volume = 0.3;
    audio.play().catch(() => {
        // Ignore if audio playback fails
    });
}

/**
 * Animate progress bars
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.transition = 'width 1s ease-out';
                    bar.style.width = width;
                }, 100);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => observer.observe(bar));
}

/**
 * Show milestone details modal
 */
function showMilestoneDetails(milestoneId) {
    // This would fetch and display detailed milestone information
    console.log('Showing details for milestone:', milestoneId);
}

/**
 * Filter milestones by category
 */
function filterMilestones(category) {
    const cards = document.querySelectorAll('.milestone-card');
    
    cards.forEach(card => {
        if (category === 'all' || card.dataset.category === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Sort achievements
 */
function sortAchievements(sortBy) {
    const container = document.querySelector('.achievements-list');
    if (!container) return;
    
    const items = Array.from(container.children);
    
    items.sort((a, b) => {
        if (sortBy === 'date') {
            return new Date(b.dataset.date) - new Date(a.dataset.date);
        } else if (sortBy === 'points') {
            return parseInt(b.dataset.points) - parseInt(a.dataset.points);
        }
        return 0;
    });
    
    items.forEach(item => container.appendChild(item));
}

/**
 * Calculate progress percentage
 */
function calculateProgress(current, target) {
    return Math.min(Math.round((current / target) * 100), 100);
}

/**
 * Format large numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Refresh gamification data
 */
async function refreshGamificationData() {
    try {
        const response = await fetch('/game/api/progress');
        if (response.ok) {
            const data = await response.json();
            updateDashboard(data);
        }
    } catch (error) {
        console.error('Failed to refresh gamification data:', error);
    }
}

/**
 * Update dashboard with new data
 */
function updateDashboard(data) {
    // Update points
    const pointsElement = document.querySelector('[data-stat="points"]');
    if (pointsElement) {
        pointsElement.textContent = formatNumber(data.total_points);
    }
    
    // Update level
    const levelElement = document.querySelector('[data-stat="level"]');
    if (levelElement) {
        levelElement.textContent = data.current_level;
    }
    
    // Update streak
    const streakElement = document.querySelector('[data-stat="streak"]');
    if (streakElement) {
        streakElement.textContent = data.streak_days;
    }
    
    // Update progress bar
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar && data.next_level_xp) {
        const progress = (data.experience_points / data.next_level_xp) * 100;
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';
    }
}

// Export functions for use in other scripts
window.gamification = {
    showCelebration,
    filterMilestones,
    sortAchievements,
    refreshGamificationData
};