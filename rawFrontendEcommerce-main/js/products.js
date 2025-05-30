/**
 * Product Management for ShopEase E-commerce Website
 * Handles product display, filtering, sorting, and pagination
 */

class ProductManager {
    constructor() {
        this.products = [];
        this.filteredProducts = [];
        this.currentPage = 1;
        this.itemsPerPage = 12;
        this.currentFilters = {
            category: null,
            search: null,
            minPrice: null,
            maxPrice: null,
            sortBy: 'name-asc'
        };
        this.viewMode = 'grid'; // 'grid' or 'list'
        this.initialize();
    }

    /**
     * Initialize product manager
     */
    async initialize() {
        try {
            await this.loadProducts();
            this.initializeEventListeners();
            this.processUrlParameters();
            this.applyFilters();
            this.renderProducts();
        } catch (error) {
            console.error('Error initializing product manager:', error);
            this.showError('Failed to load products. Please try again later.');
        }
    }

    /**
     * Load products from data source
     */
    async loadProducts() {
        try {
            if (typeof window.ShopEase !== 'undefined' && window.ShopEase.utils) {
                this.products = await window.ShopEase.utils.loadProductData();
            } else {
                // Fallback method
                const response = await fetch('data/products.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.products = Array.isArray(data) ? data : data.products || [];
            }
            
            this.filteredProducts = [...this.products];
        } catch (error) {
            console.error('Error loading products:', error);
            throw new Error('Failed to load product catalog');
        }
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // View toggle buttons
        const gridViewBtn = document.getElementById('gridView');
        const listViewBtn = document.getElementById('listView');
        
        if (gridViewBtn) {
            gridViewBtn.addEventListener('click', () => this.setViewMode('grid'));
        }
        if (listViewBtn) {
            listViewBtn.addEventListener('click', () => this.setViewMode('list'));
        }

        // Items per page selector
        const itemsPerPageSelect = document.getElementById('itemsPerPage');
        if (itemsPerPageSelect) {
            itemsPerPageSelect.addEventListener('change', (e) => {
                this.itemsPerPage = parseInt(e.target.value);
                this.currentPage = 1;
                this.renderProducts();
            });
        }

        // Sort selector
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.currentFilters.sortBy = e.target.value;
                this.applyFilters();
                this.renderProducts();
            });
        }

        // Price filter
        const applyPriceBtn = document.getElementById('applyPriceFilter');
        if (applyPriceBtn) {
            applyPriceBtn.addEventListener('click', () => this.applyPriceFilter());
        }

        // Clear filters
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        // Reset search
        const resetSearchBtn = document.getElementById('resetSearch');
        if (resetSearchBtn) {
            resetSearchBtn.addEventListener('click', () => this.resetSearch());
        }

        // Retry load
        const retryLoadBtn = document.getElementById('retryLoad');
        if (retryLoadBtn) {
            retryLoadBtn.addEventListener('click', () => this.initialize());
        }

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        
        if (searchInput && searchBtn) {
            searchBtn.addEventListener('click', () => this.performSearch());
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }
    }

    /**
     * Process URL parameters for initial filtering
     */
    processUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Category filter
        const category = urlParams.get('category');
        if (category) {
            this.currentFilters.category = decodeURIComponent(category);
        }

        // Search filter
        const search = urlParams.get('search');
        if (search) {
            this.currentFilters.search = decodeURIComponent(search);
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = this.currentFilters.search;
            }
        }

        // Update category filters UI
        this.updateCategoryFilters();
    }

    /**
     * Set view mode (grid or list)
     */
    setViewMode(mode) {
        this.viewMode = mode;
        
        // Update button states
        const gridBtn = document.getElementById('gridView');
        const listBtn = document.getElementById('listView');
        
        if (gridBtn && listBtn) {
            gridBtn.classList.toggle('active', mode === 'grid');
            listBtn.classList.toggle('active', mode === 'list');
        }

        this.renderProducts();
    }

    /**
     * Apply price filter
     */
    applyPriceFilter() {
        const minPriceInput = document.getElementById('minPrice');
        const maxPriceInput = document.getElementById('maxPrice');
        
        const minPrice = minPriceInput ? parseFloat(minPriceInput.value) : null;
        const maxPrice = maxPriceInput ? parseFloat(maxPriceInput.value) : null;

        if (minPrice !== null && isNaN(minPrice)) {
            this.showError('Please enter a valid minimum price');
            return;
        }
        
        if (maxPrice !== null && isNaN(maxPrice)) {
            this.showError('Please enter a valid maximum price');
            return;
        }

        if (minPrice !== null && maxPrice !== null && minPrice > maxPrice) {
            this.showError('Minimum price cannot be greater than maximum price');
            return;
        }

        this.currentFilters.minPrice = minPrice;
        this.currentFilters.maxPrice = maxPrice;
        this.currentPage = 1;
        this.applyFilters();
        this.renderProducts();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        this.currentFilters = {
            category: null,
            search: null,
            minPrice: null,
            maxPrice: null,
            sortBy: 'name-asc'
        };
        
        // Clear UI inputs
        const inputs = ['minPrice', 'maxPrice', 'searchInput'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) input.value = '';
        });

        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) sortSelect.value = 'name-asc';

        // Clear category checkboxes
        const categoryCheckboxes = document.querySelectorAll('input[name="category"]');
        categoryCheckboxes.forEach(checkbox => checkbox.checked = false);

        // Update URL
        const url = new URL(window.location);
        url.search = '';
        window.history.replaceState({}, '', url);

        this.currentPage = 1;
        this.applyFilters();
        this.renderProducts();
    }

    /**
     * Reset search
     */
    resetSearch() {
        this.currentFilters.search = null;
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.value = '';
        
        this.currentPage = 1;
        this.applyFilters();
        this.renderProducts();
    }

    /**
     * Perform search
     */
    performSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        const searchTerm = searchInput.value.trim();
        this.currentFilters.search = searchTerm || null;
        this.currentPage = 1;
        this.applyFilters();
        this.renderProducts();
    }

    /**
     * Apply filters to products
     */
    applyFilters() {
        let filtered = [...this.products];

        // Category filter
        if (this.currentFilters.category) {
            filtered = filtered.filter(product => 
                product.category === this.currentFilters.category
            );
        }

        // Search filter
        if (this.currentFilters.search) {
            const searchTerm = this.currentFilters.search.toLowerCase();
            filtered = filtered.filter(product => 
                product.name.toLowerCase().includes(searchTerm) ||
                product.category.toLowerCase().includes(searchTerm) ||
                (product.description && product.description.toLowerCase().includes(searchTerm))
            );
        }

        // Price filters
        if (this.currentFilters.minPrice !== null) {
            filtered = filtered.filter(product => product.price >= this.currentFilters.minPrice);
        }
        if (this.currentFilters.maxPrice !== null) {
            filtered = filtered.filter(product => product.price <= this.currentFilters.maxPrice);
        }

        // Apply sorting
        filtered = this.sortProducts(filtered, this.currentFilters.sortBy);

        this.filteredProducts = filtered;
    }

    /**
     * Sort products
     */
    sortProducts(products, sortBy) {
        const sorted = [...products];
        
        switch (sortBy) {
            case 'name-asc':
                return sorted.sort((a, b) => a.name.localeCompare(b.name));
            case 'name-desc':
                return sorted.sort((a, b) => b.name.localeCompare(a.name));
            case 'price-asc':
                return sorted.sort((a, b) => a.price - b.price);
            case 'price-desc':
                return sorted.sort((a, b) => b.price - a.price);
            default:
                return sorted;
        }
    }

    /**
     * Render products
     */
    renderProducts() {
        this.updateProductCount();
        
        if (this.filteredProducts.length === 0) {
            this.showNoProducts();
            return;
        }

        this.hideNoProducts();
        this.hideError();
        
        const paginatedProducts = this.getPaginatedProducts();
        
        if (this.viewMode === 'grid') {
            this.renderGridView(paginatedProducts);
        } else {
            this.renderListView(paginatedProducts);
        }
        
        this.renderPagination();
    }

    /**
     * Get paginated products for current page
     */
    getPaginatedProducts() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        return this.filteredProducts.slice(startIndex, endIndex);
    }

    /**
     * Render grid view
     */
    renderGridView(products) {
        const container = document.getElementById('productsGrid');
        if (!container) return;

        container.className = 'row g-4';
        container.innerHTML = products.map(product => 
            this.createProductCard(product)
        ).join('');

        this.addProductEventListeners();
    }

    /**
     * Render list view
     */
    renderListView(products) {
        const container = document.getElementById('productsGrid');
        if (!container) return;

        container.className = 'product-list';
        container.innerHTML = products.map(product => 
            this.createProductListItem(product)
        ).join('');

        this.addProductEventListeners();
    }

    /**
     * Create product card for grid view
     */
    createProductCard(product) {
        return `
            <div class="col-lg-4 col-md-6">
                <div class="card product-card h-100">
                    <div class="product-image-placeholder">
                        <i class="fas fa-image fa-2x text-muted"></i>
                        <p class="text-muted mt-2 mb-0">Product Image</p>
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h6 class="card-title">
                            <a href="product-detail.html?id=${product.id}" class="text-decoration-none text-dark">
                                ${this.escapeHtml(product.name)}
                            </a>
                        </h6>
                        <p class="card-text text-muted small mb-2">${this.escapeHtml(product.category)}</p>
                        ${product.description ? `<p class="card-text text-muted small">${this.escapeHtml(product.description.substring(0, 100))}${product.description.length > 100 ? '...' : ''}</p>` : ''}
                        <div class="mt-auto">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="h6 text-primary mb-0">$${product.price.toFixed(2)}</span>
                            </div>
                            <button class="btn btn-primary btn-sm w-100 add-to-cart-btn" 
                                    data-product-id="${product.id}">
                                <i class="fas fa-shopping-cart me-1"></i>Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create product list item for list view
     */
    createProductListItem(product) {
        return `
            <div class="product-list-item">
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <div class="product-image-placeholder-sm">
                            <i class="fas fa-image text-muted"></i>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6 class="mb-1">
                            <a href="product-detail.html?id=${product.id}" class="text-decoration-none text-dark">
                                ${this.escapeHtml(product.name)}
                            </a>
                        </h6>
                        <p class="text-muted small mb-1">Category: ${this.escapeHtml(product.category)}</p>
                        ${product.description ? `<p class="text-muted small mb-0">${this.escapeHtml(product.description.substring(0, 150))}${product.description.length > 150 ? '...' : ''}</p>` : ''}
                    </div>
                    <div class="col-md-2 text-center">
                        <span class="h6 text-primary">$${product.price.toFixed(2)}</span>
                    </div>
                    <div class="col-md-2 text-end">
                        <button class="btn btn-primary btn-sm add-to-cart-btn" 
                                data-product-id="${product.id}">
                            <i class="fas fa-shopping-cart me-1"></i>Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Add event listeners to product elements
     */
    addProductEventListeners() {
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        addToCartButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = parseInt(e.target.closest('button').dataset.productId);
                this.addToCart(productId, e.target.closest('button'));
            });
        });
    }

    /**
     * Add product to cart
     */
    async addToCart(productId, buttonElement) {
        try {
            const product = this.products.find(p => p.id === productId);
            if (!product) {
                this.showError('Product not found');
                return;
            }

            if (window.cart) {
                window.cart.addItem(product, 1);
                
                // Update cart counter
                if (window.ShopEase && window.ShopEase.utils) {
                    window.ShopEase.utils.updateCartCounter();
                    window.ShopEase.utils.showSuccessMessage('Product added to cart');
                }

                // Visual feedback
                const originalContent = buttonElement.innerHTML;
                buttonElement.innerHTML = '<i class="fas fa-check me-1"></i>Added!';
                buttonElement.classList.add('btn-success');
                buttonElement.classList.remove('btn-primary');
                buttonElement.disabled = true;
                
                setTimeout(() => {
                    buttonElement.innerHTML = originalContent;
                    buttonElement.classList.remove('btn-success');
                    buttonElement.classList.add('btn-primary');
                    buttonElement.disabled = false;
                }, 2000);
            } else {
                this.showError('Cart is not available');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showError('Failed to add product to cart: ' + error.message);
        }
    }

    /**
     * Update product count display
     */
    updateProductCount() {
        const productCountElement = document.getElementById('productCount');
        if (productCountElement) {
            const totalProducts = this.filteredProducts.length;
            const startItem = totalProducts > 0 ? ((this.currentPage - 1) * this.itemsPerPage) + 1 : 0;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, totalProducts);
            
            if (totalProducts === 0) {
                productCountElement.textContent = 'No products found';
            } else {
                productCountElement.textContent = `Showing ${startItem}-${endItem} of ${totalProducts} products`;
            }
        }
    }

    /**
     * Render pagination
     */
    renderPagination() {
        const paginationContainer = document.getElementById('pagination');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(this.filteredProducts.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        const currentPage = this.currentPage;
        let paginationHTML = '';

        // Previous button
        paginationHTML += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>
        `;

        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
            paginationHTML += '<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>';
            if (startPage > 2) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }

        // Next button
        paginationHTML += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>
        `;

        paginationContainer.innerHTML = paginationHTML;

        // Add click listeners to pagination links
        paginationContainer.querySelectorAll('a.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage && page >= 1 && page <= totalPages) {
                    this.currentPage = page;
                    this.renderProducts();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
        });
    }

    /**
     * Update category filters
     */
    updateCategoryFilters() {
        const categoryFiltersContainer = document.getElementById('categoryFilters');
        if (!categoryFiltersContainer) return;

        const categories = [...new Set(this.products.map(p => p.category))].sort();
        
        if (categories.length === 0) {
            categoryFiltersContainer.innerHTML = '<p class="text-muted small">No categories available</p>';
            return;
        }

        categoryFiltersContainer.innerHTML = categories.map(category => `
            <div class="form-check">
                <input class="form-check-input" type="radio" name="category" 
                       id="category-${this.slugify(category)}" value="${category}"
                       ${this.currentFilters.category === category ? 'checked' : ''}>
                <label class="form-check-label" for="category-${this.slugify(category)}">
                    ${this.escapeHtml(category)}
                </label>
            </div>
        `).join('');

        // Add event listeners
        categoryFiltersContainer.querySelectorAll('input[name="category"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.currentFilters.category = e.target.checked ? e.target.value : null;
                this.currentPage = 1;
                this.applyFilters();
                this.renderProducts();
            });
        });
    }

    /**
     * Show no products message
     */
    showNoProducts() {
        const noProductsElement = document.getElementById('noProductsMessage');
        const productsContainer = document.getElementById('productsContainer');
        
        if (noProductsElement) noProductsElement.classList.remove('d-none');
        if (productsContainer) productsContainer.style.display = 'none';
        
        // Hide pagination
        const pagination = document.getElementById('pagination');
        if (pagination) pagination.innerHTML = '';
    }

    /**
     * Hide no products message
     */
    hideNoProducts() {
        const noProductsElement = document.getElementById('noProductsMessage');
        const productsContainer = document.getElementById('productsContainer');
        
        if (noProductsElement) noProductsElement.classList.add('d-none');
        if (productsContainer) productsContainer.style.display = 'block';
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.classList.remove('d-none');
            const messageElement = errorElement.querySelector('p');
            if (messageElement) {
                messageElement.textContent = message;
            }
        }
        
        // Hide other elements
        this.hideNoProducts();
        const productsContainer = document.getElementById('productsContainer');
        if (productsContainer) productsContainer.style.display = 'none';
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.classList.add('d-none');
        }
    }

    /**
     * Utility functions
     */
    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    slugify(text) {
        return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }
}

// Initialize product manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('products.html')) {
        window.productManager = new ProductManager();
    }
});

// Make ProductManager available globally
window.ProductManager = ProductManager;
