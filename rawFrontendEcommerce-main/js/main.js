/**
 * Main JavaScript file for ShopEase E-commerce Website
 * Handles global functionality, navigation, and application initialization
 */

// Global application state
window.ShopEase = {
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
        updateCartCounter();
        loadCategories();
        
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
    } catch (error) {
        console.error('Error initializing application:', error);
        showErrorMessage('Failed to initialize application. Please refresh the page.');
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
        case 'products.html':
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
        if (e.key === 'shopease_cart') {
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
        const url = new URL('products.html', window.location.origin);
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
 * Show/hide loading overlay
 */
function showLoading(show = true) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay) return;
    
    ShopEase.state.isLoading = show;
    
    if (show) {
        loadingOverlay.style.opacity = '1';
        loadingOverlay.style.visibility = 'visible';
        document.body.style.overflow = 'hidden';
    } else {
        loadingOverlay.style.opacity = '0';
        loadingOverlay.style.visibility = 'hidden';
        document.body.style.overflow = '';
    }
}

/**
 * Initialize error handling
 */
function initializeErrorHandling() {
    // Global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        if (!ShopEase.state.isLoading) {
            showErrorMessage('An unexpected error occurred. Please try again.');
        }
    });
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        if (!ShopEase.state.isLoading) {
            showErrorMessage('Failed to load data. Please check your connection and try again.');
        }
    });
}

/**
 * Show error message
 */
function showErrorMessage(message, duration = 5000) {
    // Create or update error toast
    let errorToast = document.getElementById('errorToast');
    
    if (!errorToast) {
        errorToast = document.createElement('div');
        errorToast.id = 'errorToast';
        errorToast.className = 'toast position-fixed top-0 end-0 m-3';
        errorToast.style.zIndex = '10000';
        errorToast.innerHTML = `
            <div class="toast-header bg-danger text-white">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong class="me-auto">Error</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;
        document.body.appendChild(errorToast);
    } else {
        errorToast.querySelector('.toast-body').textContent = message;
    }
    
    // Show toast
    const toast = new bootstrap.Toast(errorToast, { delay: duration });
    toast.show();
}

/**
 * Show success message
 */
function showSuccessMessage(message, duration = 3000) {
    let successToast = document.getElementById('successToast');
    
    if (!successToast) {
        successToast = document.createElement('div');
        successToast.id = 'successToast';
        successToast.className = 'toast position-fixed top-0 end-0 m-3';
        successToast.style.zIndex = '10000';
        successToast.innerHTML = `
            <div class="toast-header bg-success text-white">
                <i class="fas fa-check-circle me-2"></i>
                <strong class="me-auto">Success</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;
        document.body.appendChild(successToast);
    } else {
        successToast.querySelector('.toast-body').textContent = message;
    }
    
    const toast = new bootstrap.Toast(successToast, { delay: duration });
    toast.show();
}

/**
 * Update cart counter in navigation
 */
function updateCartCounter() {
    const cartCountElements = document.querySelectorAll('#cartCount');
    const cart = getCart();
    const totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
    
    cartCountElements.forEach(element => {
        element.textContent = totalItems;
        element.style.display = totalItems > 0 ? 'inline' : 'none';
    });
}

/**
 * Load categories for navigation
 */
async function loadCategories() {
    try {
        const categories = await getCategories();
        updateCategoriesDropdown(categories);
        ShopEase.state.categories = categories;
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

/**
 * Update categories dropdown in navigation
 */
function updateCategoriesDropdown(categories) {
    const categoriesMenu = document.getElementById('categoriesMenu');
    if (!categoriesMenu) return;
    
    if (categories.length === 0) {
        categoriesMenu.innerHTML = '<li><span class="dropdown-item text-muted">No categories available</span></li>';
        return;
    }
    
    categoriesMenu.innerHTML = categories.map(category => `
        <li>
            <a class="dropdown-item" href="products.html?category=${encodeURIComponent(category)}">
                ${escapeHtml(category)}
            </a>
        </li>
    `).join('');
}

/**
 * Get categories from data
 */
async function getCategories() {
    try {
        const products = await loadProductData();
        const categories = [...new Set(products.map(product => product.category))];
        return categories.filter(category => category).sort();
    } catch (error) {
        console.error('Error getting categories:', error);
        return [];
    }
}

/**
 * Load product data from JSON file
 */
async function loadProductData() {
    try {
        const response = await fetch('data/products.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return Array.isArray(data) ? data : data.products || [];
    } catch (error) {
        console.error('Error loading product data:', error);
        throw new Error('Failed to load product catalog');
    }
}

/**
 * Page-specific initialization functions
 */
function initializeHomePage() {
    loadFeaturedCategories();
    loadFeaturedProducts();
    loadBrands();
    initializeProductFilters();
    initializeAnimations();
    initializeNewsletterForm();
}

function initializeProductsPage() {
    // Products page initialization handled in products.js
}

function initializeProductDetailPage() {
    // Product detail page initialization handled in product-detail.html
}

function initializeCartPage() {
    // Cart page initialization handled in cart.html
}

/**
 * Load featured categories for home page
 */
async function loadFeaturedCategories() {
    const container = document.getElementById('featuredCategories');
    if (!container) return;
    
    try {
        const categories = await getCategories();
        const featuredCategories = categories.slice(0, 6); // Show first 6 categories
        
        if (featuredCategories.length === 0) {
            container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No categories available at the moment.</p></div>';
            return;
        }
        
        container.innerHTML = featuredCategories.map(category => `
            <div class="col-lg-2 col-md-4 col-sm-6">
                <a href="products.html?category=${encodeURIComponent(category)}" class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-${getCategoryIcon(category)}"></i>
                    </div>
                    <h5>${escapeHtml(category)}</h5>
                </a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading featured categories:', error);
        container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">Unable to load categories. Please try again later.</p></div>';
    }
}

/**
 * Load featured products for home page
 */
async function loadFeaturedProducts() {
    const container = document.getElementById('featuredProducts');
    if (!container) return;
    
    try {
        const products = await loadProductData();
        const featuredProducts = products.slice(0, 8); // Show first 8 products
        
        if (featuredProducts.length === 0) {
            container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">No products available at the moment.</p></div>';
            return;
        }
        
        container.innerHTML = featuredProducts.map(product => createProductCard(product)).join('');
    } catch (error) {
        console.error('Error loading featured products:', error);
        container.innerHTML = '<div class="col-12 text-center"><p class="text-muted">Unable to load products. Please try again later.</p></div>';
    }
}

/**
 * Get icon for category
 */
function getCategoryIcon(category) {
    const iconMap = {
        'electronics': 'laptop',
        'clothing': 'tshirt',
        'books': 'book',
        'home': 'home',
        'sports': 'futbol',
        'beauty': 'gem',
        'toys': 'gamepad',
        'automotive': 'car',
        'jewelry': 'ring',
        'music': 'music',
        'garden': 'leaf',
        'food': 'utensils'
    };
    
    const lowercaseCategory = category.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
        if (lowercaseCategory.includes(key)) {
            return icon;
        }
    }
    return 'tag'; // Default icon
}

/**
 * Create product card HTML
 */
function createProductCard(product) {
    const salePrice = product.sale && product.originalPrice ? 
        `<span class="text-decoration-line-through text-muted me-2">$${product.originalPrice.toFixed(2)}</span>` : '';
    
    const badges = [];
    if (product.trending) badges.push('<div class="trending-badge">🔥 Trending</div>');
    if (product.sale) badges.push('<div class="sale-badge">Sale</div>');
    
    return `
        <div class="col-lg-3 col-md-4 col-sm-6">
            <div class="card product-card h-100" data-product-id="${product.id}" data-trending="${product.trending}" data-sale="${product.sale}">
                ${badges.join('')}
                <button class="wishlist-btn" title="Add to Wishlist">
                    <i class="far fa-heart"></i>
                </button>
                <div class="product-image-placeholder">
                    <i class="fas fa-image fa-2x text-muted"></i>
                    <p class="text-muted mt-2 mb-0">Product Image</p>
                </div>
                <div class="card-body d-flex flex-column">
                    <div class="mb-2">
                        <span class="badge bg-light text-dark small">${escapeHtml(product.brand)}</span>
                    </div>
                    <h6 class="card-title">
                        <a href="product-detail.html?id=${product.id}" class="text-decoration-none text-dark">
                            ${escapeHtml(product.name)}
                        </a>
                    </h6>
                    <p class="card-text text-muted small">${escapeHtml(product.category)}</p>
                    <div class="mt-auto">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                ${salePrice}
                                <span class="h6 text-primary mb-0">$${product.price.toFixed(2)}</span>
                            </div>
                        </div>
                        <button class="btn btn-primary btn-sm w-100 btn-add-to-cart" 
                                data-product-id="${product.id}"
                                onclick="addToCartFromCard(${product.id})">
                            <i class="fas fa-shopping-cart me-1"></i>Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Load brands and display them
 */
async function loadBrands() {
    const container = document.getElementById('brandsTrack');
    if (!container) return;
    
    try {
        const data = await loadProductData();
        const brands = data.brands || [];
        
        // Duplicate brands for infinite scroll effect
        const duplicatedBrands = [...brands, ...brands];
        
        container.innerHTML = duplicatedBrands.map(brand => `
            <div class="text-center px-4">
                <div class="brand-item">
                    <i class="fas ${brand.logo} fa-3x text-muted brand-logo mb-2"></i>
                    <h6 class="text-muted">${escapeHtml(brand.name)}</h6>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

/**
 * Initialize product filters on home page
 */
function initializeProductFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            filterProducts(filter);
        });
    });
}

/**
 * Filter products based on criteria
 */
function filterProducts(filter) {
    const productCards = document.querySelectorAll('#featuredProducts .product-card');
    
    productCards.forEach(card => {
        const productId = card.dataset.productId;
        const isTrending = card.dataset.trending === 'true';
        const isOnSale = card.dataset.sale === 'true';
        
        let show = true;
        
        switch(filter) {
            case 'trending':
                show = isTrending;
                break;
            case 'sale':
                show = isOnSale;
                break;
            case 'all':
            default:
                show = true;
                break;
        }
        
        const cardContainer = card.closest('.col-lg-3, .col-md-4, .col-sm-6');
        if (cardContainer) {
            if (show) {
                cardContainer.style.display = 'block';
                cardContainer.style.opacity = '0';
                setTimeout(() => {
                    cardContainer.style.opacity = '1';
                }, 100);
            } else {
                cardContainer.style.opacity = '0';
                setTimeout(() => {
                    cardContainer.style.display = 'none';
                }, 300);
            }
        }
    });
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
async function addToCartFromCard(productId) {
    try {
        const products = await loadProductData();
        const product = products.find(p => p.id === productId);
        
        if (!product) {
            showErrorMessage('Product not found');
            return;
        }
        
        const cart = getCart();
        cart.addItem(product, 1);
        updateCartCounter();
        showSuccessMessage('Product added to cart');
        
        // Visual feedback
        const button = event.target.closest('button');
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-1"></i>Added!';
        button.classList.add('btn-success');
        button.classList.remove('btn-primary');
        button.disabled = true;
        
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
            button.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        showErrorMessage('Failed to add product to cart');
    }
}

/**
 * Get cart instance
 */
function getCart() {
    if (typeof window.cart === 'undefined') {
        console.error('Cart not initialized');
        return {
            addItem: () => {},
            items: [],
            getTotal: () => 0
        };
    }
    return window.cart;
}

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
window.ShopEase.utils = {
    showLoading,
    showErrorMessage,
    showSuccessMessage,
    updateCartCounter,
    createProductCard,
    escapeHtml,
    debounce,
    formatCurrency,
    isValidEmail,
    isMobile,
    loadProductData,
    getCategories
};
