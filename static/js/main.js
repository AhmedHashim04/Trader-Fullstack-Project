/**
 * Main JavaScript file for ShopEase E-commerce Website
 * Handles global functionality, navigation, and application initialization
 */

// Global application state
window.ShopEase = {
    config: {
        itemsPerPage: 12,
        maxCartItems: 99,
        shippingThreshold: 50,
        taxRate: 0.08
    }
};

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    try {
        initializeNavigation();
        initializeLoadingOverlay();
        initializeErrorHandling();
        

    } catch (error) {
        console.error('Error initializing application:', error);
        showErrorMessage('Failed to initialize application. Please refresh the page.');
    }
}


/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    

/**
 * Handle search functionality
 */
function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm) {
        // Redirect to products page with search parameter
        const url = new URL('products.html', window.location.origin);
        url.searchParams.set('search', searchTerm);
        window.location.href = url.toString();
    }
}


/**
 * Initialize product filters on home page
 */

function filterProducts(filter) {
    const products = document.querySelectorAll('#featuredProducts .product-card');
    products.forEach(product => {
        const isTrending = product.dataset.trending === 'true';
        const tag = product.dataset.tag; // Assuming 'tag' is a dataset attribute

        if (filter === 'all') {
            product.style.display = 'block';
        } else if (filter === 'trending' && isTrending) {
            product.style.display = 'block';
        } else if (filter === tag) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });

    const buttons = document.querySelectorAll('.btn-group button');
    buttons.forEach(button => button.classList.remove('active'));
    document.querySelector(`.btn-group button[data-filter="${filter}"]`).classList.add('active');
}

/**
 * Initialize animations and interactive elements
 */
function initializeAnimations() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.product-card, .category-card, .feature-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
    
    // Wishlist button functionality
    document.addEventListener('click', function(e) {
        if (e.target.closest('.wishlist-btn')) {
            const wishlistBtn = e.target.closest('.wishlist-btn');
            const icon = wishlistBtn.querySelector('i');
            
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                wishlistBtn.style.background = 'hsl(var(--danger-color))';
                wishlistBtn.style.color = 'white';
                showSuccessMessage('Added to wishlist');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                wishlistBtn.style.background = 'rgba(255, 255, 255, 0.9)';
                wishlistBtn.style.color = '';
                showSuccessMessage('Removed from wishlist');
            }
        }
    });
}

/**
 * Debounce function for performance optimization
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
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Check if device is mobile
 */
function isMobile() {
    return window.innerWidth <= 768;
}

/**
 * Initialize newsletter form
 */
function initializeNewsletterForm() {
    const newsletterForm = document.getElementById('newsletterForm');
    if (!newsletterForm) return;
    
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const emailInput = this.querySelector('input[type="email"]');
        const submitBtn = this.querySelector('button[type="submit"]');
        const email = emailInput.value.trim();
        
        if (!email || !isValidEmail(email)) {
            showErrorMessage('Please enter a valid email address');
            return;
        }
        
        // Simulate newsletter signup
        const originalBtnContent = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Subscribing...';
        submitBtn.disabled = true;
        
        setTimeout(() => {
            submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Subscribed!';
            submitBtn.classList.remove('btn-light');
            submitBtn.classList.add('btn-success');
            emailInput.value = '';
            
            showSuccessMessage('Welcome! You\'ve been subscribed to our newsletter.');
            
            setTimeout(() => {
                submitBtn.innerHTML = originalBtnContent;
                submitBtn.classList.remove('btn-success');
                submitBtn.classList.add('btn-light');
                submitBtn.disabled = false;
            }, 3000);
        }, 1500);
    });
}

// Export functions for global use
window.ShopEase.utils = {
    debounce,
    formatCurrency,
    isValidEmail,
    isMobile,
};
}
