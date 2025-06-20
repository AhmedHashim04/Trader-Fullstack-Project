// Global application state
window.Trader = {
    config: {
        apiEndpoint: '/api',
        itemsPerPage: 12,
        maxCartItems: 99,
        shippingThreshold: 50,
        taxRate: 0.08
    },
    state: {
        currentPage: 1,
        isLoading: false,
        categories: [],
        products: [],
        filteredProducts: []
    }
};



// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    const gridViewBtn = document.getElementById('gridView');
    const listViewBtn = document.getElementById('listView');
    const productsContainer = document.getElementById('productsContainer'); // Define productsContainer

    if (gridViewBtn && listViewBtn && productsContainer) {
        gridViewBtn.addEventListener('click', function () {
            window.location.href = '?view_mode=grid';
            productsContainer.classList.remove('list-view');
            productsContainer.classList.add('grid-view');
            gridViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');

        });

        listViewBtn.addEventListener('click', function () {
            window.location.href = '?view_mode=list';
            productsContainer.classList.remove('grid-view');
            productsContainer.classList.add('list-view');
            listViewBtn.classList.add('active');
            gridViewBtn.classList.remove('active');
        });
    }
});


/**

 * Initialize the application
 */
function initializeApp() {
    try {

        
        // Page-specific initialization
        const currentPage = getCurrentPage();
        switch(currentPage) {
            case 'home':
                initializeHomePage();
                break;
            case 'products':
                initializeProductsPage();
                break;
            case 'product-detail':
                initializeProductDetailPage();
                break;
            case 'cart':
                initializeCartPage();
                break;
        }
    } 
    catch (error) {
        console.error('Initialization error:', error);
    } 

}
/**
 * Get current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop() || 'index.html';
    
    switch(filename) {
        case 'index.html':
        case '':
            return 'home';
        case 'products':
            return 'products';
        case 'product-detail.html':
            return 'product-detail';
        case 'cart.html':
            return 'cart';
        case 'about.html':
            return 'about';
        case 'contact.html':
            return 'contact';
        default:
            return 'unknown';
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
    
    // Cart counter update
    window.addEventListener('storage', function(e) {
        if (e.key === 'Trader_cart') {
            updateCartCounter();
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
        const url = new URL('/products/', window.location.origin);
        url.searchParams.set('search', searchTerm);
        window.location.href = url.toString();
    }
}

/**
 * Initialize loading overlay
 */
function initializeLoadingOverlay() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay) return;
    
    // Add loading overlay styles if not present
    if (!loadingOverlay.style.position) {
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        `;
    }
}

/**
 * Page-specific initialization functions
 */
function initializeHomePage() {
    initializeProductFilters();
    initializeAnimations();
    initializeNewsletterForm();
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
 * Add to cart from product card
 */

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
window.Trader.utils = {
    escapeHtml,
    debounce,
    formatCurrency,
    isValidEmail,
    isMobile,
};
