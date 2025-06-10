/**
 * Shopping Cart Management for ShopEase E-commerce Website
 * Handles cart operations, localStorage persistence, and cart UI updates
 */

class ShoppingCart {
    constructor() {
        this.storageKey = 'shopease_cart';
        this.items = [];
        this.loadFromStorage();
        this.initializeEventListeners();
    }

    /**
     * Load cart data from localStorage
     */
    loadFromStorage() {
        try {
            const storedCart = localStorage.getItem(this.storageKey);
            if (storedCart) {
                const cartData = JSON.parse(storedCart);
                this.items = Array.isArray(cartData.items) ? cartData.items : [];
                this.validateCartItems();
            }
        } catch (error) {
            console.error('Error loading cart from storage:', error);
            this.items = [];
        }
    }

    /**
     * Save cart data to localStorage
     */
    saveToStorage() {
        try {
            const cartData = {
                items: this.items,
                updatedAt: new Date().toISOString()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(cartData));
            this.dispatchCartUpdate();
        } catch (error) {
            console.error('Error saving cart to storage:', error);
        }
    }

    /**
     * Validate cart items structure
     */
    validateCartItems() {
        this.items = this.items.filter(item => {
            return item && 
                   typeof item.id !== 'undefined' && 
                   typeof item.name === 'string' && 
                   typeof item.price === 'number' && 
                   typeof item.quantity === 'number' && 
                   item.quantity > 0;
        });
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Listen for storage changes from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                this.loadFromStorage();
                this.updateCartDisplay();
            }
        });
    }

    /**
     * Add item to cart
     */
    addItem(product, quantity = 1) {
        if (!this.isValidProduct(product)) {
            throw new Error('Invalid product data');
        }

        if (!Number.isInteger(quantity) || quantity < 1) {
            throw new Error('Invalid quantity');
        }

        const existingItemIndex = this.items.findIndex(item => item.id === product.id);
        
        if (existingItemIndex > -1) {
            // Update existing item quantity
            const newQuantity = this.items[existingItemIndex].quantity + quantity;
            if (newQuantity > 10) {
                throw new Error('Maximum quantity per item is 10');
            }
            this.items[existingItemIndex].quantity = newQuantity;
        } else {
            // Add new item
            if (this.items.length >= 50) {
                throw new Error('Cart is full. Maximum 50 different items allowed');
            }
            
            this.items.push({
                id: product.id,
                name: product.name,
                price: parseFloat(product.price),
                category: product.category,
                quantity: quantity,
                addedAt: new Date().toISOString()
            });
        }

        this.saveToStorage();
        return true;
    }

    /**
     * Remove item from cart
     */
    removeItem(productId) {
        const initialLength = this.items.length;
        this.items = this.items.filter(item => item.id !== productId);
        
        if (this.items.length !== initialLength) {
            this.saveToStorage();
            return true;
        }
        return false;
    }

    /**
     * Update item quantity
     */
    updateQuantity(productId, quantity) {
        if (!Number.isInteger(quantity) || quantity < 0) {
            throw new Error('Invalid quantity');
        }

        if (quantity === 0) {
            return this.removeItem(productId);
        }

        if (quantity > 10) {
            throw new Error('Maximum quantity per item is 10');
        }

        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity = quantity;
            this.saveToStorage();
            return true;
        }
        return false;
    }

    /**
     * Get cart items
     */
    getItems() {
        return [...this.items];
    }

    /**
     * Get item count
     */
    getItemCount() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }

    /**
     * Get subtotal
     */
    getSubtotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    /**
     * Calculate shipping cost
     */
    getShippingCost() {
        const subtotal = this.getSubtotal();
        return subtotal >= 50 ? 0 : 9.99;
    }

    /**
     * Calculate tax
     */
    getTax() {
        return this.getSubtotal() * 0.08; // 8% tax rate
    }

    /**
     * Get total price including shipping and tax
     */
    getTotal() {
        return this.getSubtotal() + this.getShippingCost() + this.getTax();
    }

    /**
     * Clear cart
     */
    clear() {
        this.items = [];
        this.saveToStorage();
        return true;
    }

    /**
     * Check if cart is empty
     */
    isEmpty() {
        return this.items.length === 0;
    }

    /**
     * Get cart summary
     */
    getSummary() {
        return {
            itemCount: this.getItemCount(),
            subtotal: this.getSubtotal(),
            shipping: this.getShippingCost(),
            tax: this.getTax(),
            total: this.getTotal(),
            isEmpty: this.isEmpty()
        };
    }

    /**
     * Validate product data
     */
    isValidProduct(product) {
        return product && 
               typeof product.id !== 'undefined' && 
               typeof product.name === 'string' && 
               typeof product.price === 'number' && 
               product.price >= 0 &&
               typeof product.category === 'string';
    }

    /**
     * Dispatch cart update event
     */
    dispatchCartUpdate() {
        const event = new CustomEvent('cartUpdated', {
            detail: this.getSummary()
        });
        window.dispatchEvent(event);
    }

    /**
     * Update cart display elements
     */
    updateCartDisplay() {
        // Update cart counter
        const cartCountElements = document.querySelectorAll('#cartCount, .cart-count');
        const itemCount = this.getItemCount();
        
        cartCountElements.forEach(element => {
            element.textContent = itemCount;
            element.style.display = itemCount > 0 ? 'inline' : 'none';
        });

        // Update cart page if we're on it
        if (window.location.pathname.includes('cart.html')) {
            this.updateCartPage();
        }
    }

    /**
     * Update cart page display
     */
    updateCartPage() {
        const cartItemsContainer = document.getElementById('cartItemsContainer');
        const emptyCartElement = document.getElementById('emptyCart');
        const cartSummaryElements = {
            subtotal: document.getElementById('subtotal'),
            shipping: document.getElementById('shipping'),
            tax: document.getElementById('tax'),
            total: document.getElementById('total')
        };

        if (this.isEmpty()) {
            if (cartItemsContainer) cartItemsContainer.style.display = 'none';
            if (emptyCartElement) emptyCartElement.classList.remove('d-none');
            return;
        }

        if (emptyCartElement) emptyCartElement.classList.add('d-none');
        if (cartItemsContainer) {
            cartItemsContainer.style.display = 'block';
            this.renderCartItems();
        }

        // Update summary
        const summary = this.getSummary();
        if (cartSummaryElements.subtotal) {
            cartSummaryElements.subtotal.textContent = `$${summary.subtotal.toFixed(2)}`;
        }
        if (cartSummaryElements.shipping) {
            cartSummaryElements.shipping.textContent = summary.shipping === 0 ? 'Free' : `$${summary.shipping.toFixed(2)}`;
        }
        if (cartSummaryElements.tax) {
            cartSummaryElements.tax.textContent = `$${summary.tax.toFixed(2)}`;
        }
        if (cartSummaryElements.total) {
            cartSummaryElements.total.textContent = `$${summary.total.toFixed(2)}`;
        }

        // Update checkout button
        const checkoutBtn = document.getElementById('checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.disabled = this.isEmpty();
        }
    }

    /**
     * Render cart items
     */
    renderCartItems() {
        const container = document.getElementById('cartItemsContainer');
        if (!container) return;

        container.innerHTML = this.items.map(item => this.createCartItemHTML(item)).join('');
        
        // Add event listeners for cart item controls
        this.items.forEach(item => {
            this.addCartItemEventListeners(item.id);
        });
    }

    /**
     * Create cart item HTML
     */
    createCartItemHTML(item) {
        return `
            <div class="cart-item p-3 border-bottom" data-item-id="${item.id}">
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <div class="product-image-placeholder-sm">
                            <i class="fas fa-image text-muted"></i>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <h6 class="mb-1">${this.escapeHtml(item.name)}</h6>
                        <small class="text-muted">Category: ${this.escapeHtml(item.category)}</small>
                        <div class="mt-1">
                            <span class="badge bg-light text-dark">$${item.price.toFixed(2)} each</span>
                        </div>
                    </div>
                    <div class="col-md-2 text-center">
                        <span class="fw-bold text-primary">$${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                    <div class="col-md-3">
                        <div class="input-group input-group-sm">
                            <button class="btn btn-outline-secondary quantity-decrease" 
                                    type="button" data-item-id="${item.id}"
                                    ${item.quantity <= 1 ? 'disabled' : ''}>
                                <i class="fas fa-minus"></i>
                            </button>
                            <input type="number" class="form-control text-center quantity-input" 
                                   value="${item.quantity}" min="1" max="10" 
                                   data-item-id="${item.id}">
                            <button class="btn btn-outline-secondary quantity-increase" 
                                    type="button" data-item-id="${item.id}"
                                    ${item.quantity >= 10 ? 'disabled' : ''}>
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="col-md-1 text-end">
                        <button class="btn btn-outline-danger btn-sm remove-item" 
                                data-item-id="${item.id}" title="Remove item">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Add event listeners for cart item controls
     */
    addCartItemEventListeners(itemId) {
        // Quantity decrease
        const decreaseBtn = document.querySelector(`[data-item-id="${itemId}"].quantity-decrease`);
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', () => {
                const item = this.items.find(i => i.id === itemId);
                if (item && item.quantity > 1) {
                    this.updateQuantity(itemId, item.quantity - 1);
                    this.updateCartDisplay();
                }
            });
        }

        // Quantity increase
        const increaseBtn = document.querySelector(`[data-item-id="${itemId}"].quantity-increase`);
        if (increaseBtn) {
            increaseBtn.addEventListener('click', () => {
                const item = this.items.find(i => i.id === itemId);
                if (item && item.quantity < 10) {
                    this.updateQuantity(itemId, item.quantity + 1);
                    this.updateCartDisplay();
                }
            });
        }

        // Quantity input
        const quantityInput = document.querySelector(`[data-item-id="${itemId}"].quantity-input`);
        if (quantityInput) {
            quantityInput.addEventListener('change', (e) => {
                const newQuantity = parseInt(e.target.value);
                if (newQuantity >= 1 && newQuantity <= 10) {
                    this.updateQuantity(itemId, newQuantity);
                    this.updateCartDisplay();
                } else {
                    // Reset to current quantity if invalid
                    const item = this.items.find(i => i.id === itemId);
                    e.target.value = item ? item.quantity : 1;
                }
            });
        }

        // Remove item
        const removeBtn = document.querySelector(`[data-item-id="${itemId}"].remove-item`);
        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                if (confirm('Are you sure you want to remove this item from your cart?')) {
                    this.removeItem(itemId);
                    this.updateCartDisplay();
                    
                    // Show success message
                    if (typeof window.ShopEase !== 'undefined' && window.ShopEase.utils) {
                        window.ShopEase.utils.showSuccessMessage('Item removed from cart');
                    }
                }
            });
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Export cart data
     */
    export() {
        return {
            items: this.getItems(),
            summary: this.getSummary(),
            exportedAt: new Date().toISOString()
        };
    }

    /**
     * Import cart data
     */
    import(cartData) {
        if (!cartData || !Array.isArray(cartData.items)) {
            throw new Error('Invalid cart data format');
        }

        this.items = cartData.items.filter(item => this.isValidProduct(item));
        this.validateCartItems();
        this.saveToStorage();
        this.updateCartDisplay();
    }
}

// Initialize cart when script loads
window.cart = new ShoppingCart();

// Listen for cart updates and update display
window.addEventListener('cartUpdated', function(event) {
    console.log('Cart updated:', event.detail);
});

// Update cart display when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.cart.updateCartDisplay();
});

// Export cart class for potential external use
window.ShoppingCart = ShoppingCart;
