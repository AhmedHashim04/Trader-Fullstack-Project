/**
 * Search functionality for ShopEase E-commerce Website
 * Handles product search, suggestions, and search history
 */

class SearchManager {
    constructor() {
        this.searchHistory = [];
        this.searchSuggestions = [];
        this.maxHistoryItems = 10;
        this.maxSuggestions = 8;
        this.debounceDelay = 300;
        this.storageKey = 'shopease_search_history';
        
        this.loadSearchHistory();
        this.initializeSearch();
    }

    /**
     * Initialize search functionality
     */
    initializeSearch() {
        const searchInputs = document.querySelectorAll('#searchInput, .search-input');
        const searchButtons = document.querySelectorAll('#searchBtn, .search-btn');

        // Add event listeners to all search inputs
        searchInputs.forEach(input => {
            input.addEventListener('input', this.debounce((e) => {
                this.handleSearchInput(e.target.value, e.target);
            }, this.debounceDelay));

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
                this.handleKeyboardNavigation(e);
            });

            input.addEventListener('focus', (e) => {
                this.showSearchDropdown(e.target);
            });

            input.addEventListener('blur', (e) => {
                // Delay hiding to allow clicking on suggestions
                setTimeout(() => {
                    this.hideSearchDropdown(e.target);
                }, 200);
            });
        });

        // Add event listeners to search buttons
        searchButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const input = this.findAssociatedInput(e.target);
                if (input) {
                    this.performSearch(input.value);
                }
            });
        });

        // Initialize search suggestions dropdown
        this.initializeSearchDropdown();
    }

    /**
     * Handle search input changes
     */
    async handleSearchInput(query, inputElement) {
        const trimmedQuery = query.trim();
        
        if (trimmedQuery.length < 2) {
            this.hideSearchDropdown(inputElement);
            return;
        }

        try {
            const suggestions = await this.generateSuggestions(trimmedQuery);
            this.displaySuggestions(suggestions, inputElement);
        } catch (error) {
            console.error('Error generating suggestions:', error);
        }
    }

    /**
     * Generate search suggestions
     */
    async generateSuggestions(query) {
        try {
            const products = await this.loadProducts();
            const suggestions = new Set();
            const queryLower = query.toLowerCase();

            // Add product name matches
            products.forEach(product => {
                const name = product.name.toLowerCase();
                if (name.includes(queryLower)) {
                    suggestions.add(product.name);
                }
            });

            // Add category matches
            products.forEach(product => {
                const category = product.category.toLowerCase();
                if (category.includes(queryLower)) {
                    suggestions.add(product.category);
                }
            });

            // Add search history matches
            this.searchHistory.forEach(historyItem => {
                const historyLower = historyItem.toLowerCase();
                if (historyLower.includes(queryLower)) {
                    suggestions.add(historyItem);
                }
            });

            // Convert to array and limit results
            return Array.from(suggestions).slice(0, this.maxSuggestions);
        } catch (error) {
            console.error('Error generating suggestions:', error);
            return [];
        }
    }

    /**
     * Display search suggestions
     */
    displaySuggestions(suggestions, inputElement) {
        const dropdown = this.getOrCreateDropdown(inputElement);
        
        if (suggestions.length === 0) {
            this.hideSearchDropdown(inputElement);
            return;
        }

        const suggestionItems = suggestions.map((suggestion, index) => `
            <div class="search-suggestion-item" data-index="${index}" data-suggestion="${this.escapeHtml(suggestion)}">
                <i class="fas fa-search text-muted me-2"></i>
                <span>${this.highlightMatch(suggestion, inputElement.value)}</span>
            </div>
        `).join('');

        // Add search history section if available
        let historySection = '';
        if (this.searchHistory.length > 0) {
            const recentSearches = this.searchHistory.slice(0, 3);
            historySection = `
                <div class="search-history-section">
                    <div class="search-section-header">Recent Searches</div>
                    ${recentSearches.map((item, index) => `
                        <div class="search-suggestion-item history-item" data-suggestion="${this.escapeHtml(item)}">
                            <i class="fas fa-history text-muted me-2"></i>
                            <span>${this.escapeHtml(item)}</span>
                            <button class="btn btn-sm btn-link remove-history" data-history="${this.escapeHtml(item)}">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        dropdown.innerHTML = `
            <div class="search-suggestions-section">
                <div class="search-section-header">Suggestions</div>
                ${suggestionItems}
            </div>
            ${historySection}
        `;

        this.showSearchDropdown(inputElement);
        this.addSuggestionEventListeners(dropdown, inputElement);
    }

    /**
     * Highlight matching text in suggestions
     */
    highlightMatch(text, query) {
        if (!query.trim()) return this.escapeHtml(text);
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return this.escapeHtml(text).replace(regex, '<strong>$1</strong>');
    }

    /**
     * Add event listeners to suggestion items
     */
    addSuggestionEventListeners(dropdown, inputElement) {
        // Suggestion item clicks
        dropdown.querySelectorAll('.search-suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const suggestion = item.dataset.suggestion;
                inputElement.value = suggestion;
                this.performSearch(suggestion);
                this.hideSearchDropdown(inputElement);
            });
        });

        // Remove history item buttons
        dropdown.querySelectorAll('.remove-history').forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const historyItem = button.dataset.history;
                this.removeFromHistory(historyItem);
                this.handleSearchInput(inputElement.value, inputElement);
            });
        });
    }

    /**
     * Handle keyboard navigation in suggestions
     */
    handleKeyboardNavigation(event) {
        const dropdown = this.getDropdownForInput(event.target);
        if (!dropdown || dropdown.style.display === 'none') return;

        const suggestions = dropdown.querySelectorAll('.search-suggestion-item');
        const currentActive = dropdown.querySelector('.search-suggestion-item.active');
        let activeIndex = currentActive ? Array.from(suggestions).indexOf(currentActive) : -1;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                activeIndex = (activeIndex + 1) % suggestions.length;
                this.setActiveSuggestion(suggestions, activeIndex);
                break;
            case 'ArrowUp':
                event.preventDefault();
                activeIndex = activeIndex <= 0 ? suggestions.length - 1 : activeIndex - 1;
                this.setActiveSuggestion(suggestions, activeIndex);
                break;
            case 'Enter':
                if (currentActive) {
                    event.preventDefault();
                    currentActive.click();
                }
                break;
            case 'Escape':
                this.hideSearchDropdown(event.target);
                break;
        }
    }

    /**
     * Set active suggestion for keyboard navigation
     */
    setActiveSuggestion(suggestions, activeIndex) {
        suggestions.forEach((item, index) => {
            item.classList.toggle('active', index === activeIndex);
        });
    }

    /**
     * Perform search
     */
    performSearch(query) {
        const trimmedQuery = query.trim();
        
        if (!trimmedQuery) {
            this.showError('Please enter a search term');
            return;
        }

        // Add to search history
        this.addToHistory(trimmedQuery);

        // Redirect to products page with search parameter
        const url = new URL('products.html', window.location.origin);
        url.searchParams.set('search', trimmedQuery);
        
        // If we're already on products page, update the current page
        if (window.location.pathname.includes('products.html')) {
            window.location.search = url.search;
        } else {
            window.location.href = url.toString();
        }
    }

    /**
     * Add search term to history
     */
    addToHistory(query) {
        const trimmedQuery = query.trim();
        if (!trimmedQuery) return;

        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(item => 
            item.toLowerCase() !== trimmedQuery.toLowerCase()
        );

        // Add to beginning
        this.searchHistory.unshift(trimmedQuery);

        // Limit history size
        this.searchHistory = this.searchHistory.slice(0, this.maxHistoryItems);

        this.saveSearchHistory();
    }

    /**
     * Remove item from search history
     */
    removeFromHistory(query) {
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        this.saveSearchHistory();
    }

    /**
     * Clear search history
     */
    clearHistory() {
        this.searchHistory = [];
        this.saveSearchHistory();
    }

    /**
     * Load search history from localStorage
     */
    loadSearchHistory() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                this.searchHistory = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading search history:', error);
            this.searchHistory = [];
        }
    }

    /**
     * Save search history to localStorage
     */
    saveSearchHistory() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('Error saving search history:', error);
        }
    }

    /**
     * Initialize search dropdown
     */
    initializeSearchDropdown() {
        const style = document.createElement('style');
        style.textContent = `
            .search-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 0.375rem 0.375rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
                max-height: 300px;
                overflow-y: auto;
                display: none;
            }
            
            .search-section-header {
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
                font-weight: 600;
                color: #6c757d;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            
            .search-suggestion-item {
                padding: 0.75rem 1rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #f8f9fa;
                transition: background-color 0.2s;
            }
            
            .search-suggestion-item:hover,
            .search-suggestion-item.active {
                background-color: #f8f9fa;
            }
            
            .search-suggestion-item:last-child {
                border-bottom: none;
            }
            
            .search-suggestion-item .remove-history {
                margin-left: auto;
                padding: 0.25rem;
                opacity: 0.5;
            }
            
            .search-suggestion-item:hover .remove-history {
                opacity: 1;
            }
            
            .search-history-section {
                border-top: 1px solid #dee2e6;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Get or create dropdown for input
     */
    getOrCreateDropdown(inputElement) {
        let dropdown = this.getDropdownForInput(inputElement);
        
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.className = 'search-dropdown';
            
            // Position relative to input
            const inputParent = inputElement.closest('.input-group') || inputElement.parentElement;
            inputParent.style.position = 'relative';
            inputParent.appendChild(dropdown);
        }
        
        return dropdown;
    }

    /**
     * Get dropdown for specific input
     */
    getDropdownForInput(inputElement) {
        const inputParent = inputElement.closest('.input-group') || inputElement.parentElement;
        return inputParent.querySelector('.search-dropdown');
    }

    /**
     * Show search dropdown
     */
    showSearchDropdown(inputElement) {
        const dropdown = this.getDropdownForInput(inputElement);
        if (dropdown) {
            dropdown.style.display = 'block';
        }
    }

    /**
     * Hide search dropdown
     */
    hideSearchDropdown(inputElement) {
        const dropdown = this.getDropdownForInput(inputElement);
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    /**
     * Find associated input for a search button
     */
    findAssociatedInput(buttonElement) {
        const inputGroup = buttonElement.closest('.input-group');
        if (inputGroup) {
            return inputGroup.querySelector('input[type="text"], .search-input');
        }
        return null;
    }

    /**
     * Load products for suggestions
     */
    async loadProducts() {
        try {
            if (typeof window.ShopEase !== 'undefined' && window.ShopEase.utils) {
                return await window.ShopEase.utils.loadProductData();
            } else {
                const response = await fetch('data/products.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return Array.isArray(data) ? data : data.products || [];
            }
        } catch (error) {
            console.error('Error loading products for search:', error);
            return [];
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (typeof window.ShopEase !== 'undefined' && window.ShopEase.utils) {
            window.ShopEase.utils.showErrorMessage(message);
        } else {
            alert(message);
        }
    }

    /**
     * Utility functions
     */
    debounce(func, wait) {
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

    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Advanced search functionality
     */
    performAdvancedSearch(filters) {
        const url = new URL('products.html', window.location.origin);
        
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== '') {
                url.searchParams.set(key, filters[key]);
            }
        });
        
        window.location.href = url.toString();
    }

    /**
     * Get search suggestions for autocomplete
     */
    getSearchSuggestions() {
        return this.searchSuggestions;
    }

    /**
     * Get search history
     */
    getSearchHistory() {
        return [...this.searchHistory];
    }
}

// Initialize search manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.searchManager = new SearchManager();
});

// Export SearchManager for external use
window.SearchManager = SearchManager;
