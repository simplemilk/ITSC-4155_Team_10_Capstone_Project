/**
 * Index Page JavaScript
 * Handles interactive elements and animations for the landing page
 */

document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

/**
 * Initialize page functionality
 */
function initializePage() {
    initializeAnimations();
    initializeTooltips();
    initializeSmoothScrolling();
    initializeCardInteractions();
    initializePerformanceOptimizations();
    initializeAccessibility();
}

/**
 * Navigate to Financial Goals page
 */
function navigateToFinanceGoals() {
    // Try different possible routes
    const possibleRoutes = [
        '/finance-goals',
        '/goals',
        '/financial-goals'
    ];
    
    // For now, show a message and try the first route
    console.log('Navigating to Financial Goals...');
    
    // Try to navigate to the finance goals page
    try {
        window.location.href = possibleRoutes[0];
    } catch (error) {
        console.error('Error navigating to finance goals:', error);
        alert('Financial Goals feature is being set up. Please check back soon!');
    }
}

/**
 * Initialize animations and loading states
 */
function initializeAnimations() {
    // Add staggered animation delays to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Add staggered animation delays to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
    });

    // Intersection Observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements that should animate on scroll
        const animatedElements = document.querySelectorAll('.feature-card, .dashboard-card');
        animatedElements.forEach(el => observer.observe(el));
    }
}

/**
 * Initialize tooltips for dashboard cards
 */
function initializeTooltips() {
    const dashboardCards = document.querySelectorAll('.dashboard-card[data-tooltip]');
    
    dashboardCards.forEach(card => {
        const tooltipType = card.getAttribute('data-tooltip');
        const tooltipText = getTooltipText(tooltipType);
        
        if (tooltipText) {
            createTooltip(card, tooltipText);
        }
    });
}

/**
 * Get tooltip text based on type
 */
function getTooltipText(type) {
    const tooltips = {
        'dashboard': 'View your complete financial overview and recent activity',
        'transactions': 'Add, edit, and categorize your financial transactions',
        'income': 'Track all your income sources and recurring payments',
        'budget': 'Create and manage budgets to control your spending',
        'financial-goals': 'Set and track your financial goals with target dates'
    };
    
    return tooltips[type] || '';
}

/**
 * Create tooltip element
 */
function createTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-text';
    tooltip.textContent = text;
    
    element.classList.add('tooltip-container');
    element.appendChild(tooltip);
    
    // Position tooltip on hover
    element.addEventListener('mouseenter', () => {
        positionTooltip(tooltip, element);
    });
}

/**
 * Position tooltip to prevent overflow
 */
function positionTooltip(tooltip, element) {
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    // Check if tooltip would overflow viewport
    if (rect.left + tooltipRect.width > window.innerWidth) {
        tooltip.style.left = 'auto';
        tooltip.style.right = '0';
        tooltip.style.marginLeft = '0';
        tooltip.style.marginRight = '10px';
    }
    
    if (rect.top - tooltipRect.height < 0) {
        tooltip.style.bottom = 'auto';
        tooltip.style.top = '125%';
    }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL without jumping
                history.pushState(null, null, href);
            }
        });
    });
}

/**
 * Initialize card interactions and click analytics
 */
function initializeCardInteractions() {
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    const authButtons = document.querySelectorAll('.auth-btn');
    
    // Add click tracking for dashboard cards
    dashboardCards.forEach(card => {
        card.addEventListener('click', function(e) {
            const cardType = this.getAttribute('data-tooltip') || 'unknown';
            trackCardClick(cardType);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        // Add keyboard navigation
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add click tracking for auth buttons
    authButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const buttonType = this.classList.contains('btn-login') ? 'login' : 'register';
            trackButtonClick(buttonType);
            
            // Add loading state
            this.classList.add('loading');
            
            // Prevent double-clicking
            this.style.pointerEvents = 'none';
            setTimeout(() => {
                this.style.pointerEvents = '';
                this.classList.remove('loading');
            }, 2000);
        });
    });
}

/**
 * Track card clicks for analytics
 */
function trackCardClick(cardType) {
    console.log(`Dashboard card clicked: ${cardType}`);
    
    // Send analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', 'click', {
            'event_category': 'Dashboard Card',
            'event_label': cardType
        });
    }
}

/**
 * Track button clicks for analytics
 */
function trackButtonClick(buttonType) {
    console.log(`Auth button clicked: ${buttonType}`);
    
    // Send analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', 'click', {
            'event_category': 'Auth Button',
            'event_label': buttonType
        });
    }
}

/**
 * Initialize performance optimizations
 */
function initializePerformanceOptimizations() {
    // Lazy load images if any
    if ('IntersectionObserver' in window) {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    // Throttle scroll events
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            handleScroll();
        }, 16); // ~60fps
    });
}

/**
 * Handle scroll events
 */
function handleScroll() {
    const scrollY = window.scrollY;
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        // Parallax effect for hero section
        const parallaxSpeed = 0.5;
        heroSection.style.transform = `translateY(${scrollY * parallaxSpeed}px)`;
    }
    
    // Show/hide back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        if (scrollY > 500) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Add ARIA labels to interactive elements
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        if (!card.getAttribute('aria-label')) {
            const title = card.querySelector('.dashboard-title');
            if (title) {
                card.setAttribute('aria-label', `Navigate to ${title.textContent}`);
            }
        }
    });
    
    // Add role attributes
    const cardContainers = document.querySelectorAll('.dashboard-grid, .row');
    cardContainers.forEach(container => {
        if (!container.getAttribute('role')) {
            container.setAttribute('role', 'region');
        }
    });
    
    // Handle reduced motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.style.scrollBehavior = 'auto';
        
        // Disable animations
        const animatedElements = document.querySelectorAll('.dashboard-card, .feature-card, .auth-btn');
        animatedElements.forEach(element => {
            element.style.animation = 'none';
            element.style.transition = 'none';
        });
    }
    
    // Focus management for modal-like interactions
    document.addEventListener('keydown', function(e) {
        // Escape key handling
        if (e.key === 'Escape') {
            const activeTooltips = document.querySelectorAll('.tooltip-text:hover');
            activeTooltips.forEach(tooltip => {
                tooltip.style.visibility = 'hidden';
                tooltip.style.opacity = '0';
            });
        }
    });
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to throttle function calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Handle page visibility changes
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause animations when page is not visible
        document.body.classList.add('page-hidden');
    } else {
        // Resume animations when page becomes visible
        document.body.classList.remove('page-hidden');
    }
});

/**
 * Initialize error handling
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript error on index page:', e.error);
    
    // Graceful degradation - ensure basic functionality works
    const authButtons = document.querySelectorAll('.auth-btn');
    authButtons.forEach(button => {
        button.style.pointerEvents = 'auto';
        button.classList.remove('loading');
    });
});

/**
 * Export functions for testing and global access
 */
window.navigateToFinanceGoals = navigateToFinanceGoals;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializePage,
        getTooltipText,
        trackCardClick,
        trackButtonClick,
        debounce,
        throttle,
        navigateToFinanceGoals
    };
}