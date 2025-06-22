import { apiHelper } from '../../js/common/api_helper.js';
import { showToast } from '../../js/common/ui.js';

class B2BCartManager {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('b2b_cart')) || [];
        this.userProfile = null;
        this.tierDiscounts = {}; // Will be populated from the API
    }

    /**
     * Initializes the manager by loading user profile and tier discounts.
     * This must be called before any other methods are used.
     */
    async init() {
        try {
            // Fetch user profile and tier discounts in parallel for efficiency
            const [profile, tiers] = await Promise.all([
                apiHelper.get('/b2b/profile'),
                apiHelper.get('/b2b/loyalty/tiers') 
            ]);
            
            this.userProfile = profile;

            // Convert the array of tiers into a more accessible map
            this.tierDiscounts = tiers.reduce((acc, tier) => {
                acc[tier.name] = tier.discount;
                return acc;
            }, {});

        } catch (error) {
            console.error("Could not initialize B2BCartManager:", error);
            showToast('Could not load your profile or pricing data. Prices may be incorrect.', 'error');
        }
    }

    getDiscount() {
        if (this.userProfile && this.userProfile.tier && this.tierDiscounts[this.userProfile.tier]) {
            return this.tierDiscounts[this.userProfile.tier];
        }
        return 0; // No discount
    }

    calculatePrice(basePrice) {
        const discount = this.getDiscount();
        return basePrice * (1 - discount);
    }
    
    async addToCart(productId, quantity = 1) {
       try {
            const product = await apiHelper.get(`/products/${productId}`);
            const finalPrice = this.calculatePrice(product.price);

            const existingItem = this.cart.find(item => item.id === product.id);
            if (existingItem) {
                existingItem.quantity += quantity;
            } else {
                this.cart.push({
                    id: product.id,
                    name: product.name,
                    price: parseFloat(finalPrice.toFixed(2)),
                    original_price: product.price,
                    quantity: quantity,
                    imageUrl: product.image_url,
                });
            }
            this.saveCart();
            showToast(`${product.name} added to cart.`, 'success');
       } catch (error) {
           console.error('Failed to add to B2B cart:', error);
           showToast('Error adding item.', 'error');
       }
    }

    saveCart() {
        localStorage.setItem('b2b_cart', JSON.stringify(this.cart));
        // You might want to dispatch an event here to update the cart UI in the header
        document.dispatchEvent(new CustomEvent('b2bCartUpdated'));
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // --- Initialization ---
    const token = localStorage.getItem('token'); // Your B2B token key
    if (!token) {
        window.location.href = '/pro/professionnels.html';
        return;
    }

    const b2bCartManager = new B2BCartManager();
    await b2bCartManager.init();

    // --- DOM Elements ---
    const productGrid = document.getElementById('product-grid');
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const collectionFilter = document.getElementById('collection-filter');
    const specieFilter = document.getElementById('specie-filter');
    const sortBy = document.getElementById('sort-by');

    const filters = {
        search: '', category: '', collection: '',
        specie: '', sort_by: 'name_asc'
    };

    // --- Functions ---
    async function fetchProducts() {
        const query = new URLSearchParams(filters).toString();
        productGrid.innerHTML = '<p class="col-span-full text-center p-8 text-gray-500">Loading products...</p>';
        try {
            const products = await apiHelper.get(`/b2b/products?${query}`);
            renderProducts(products);
        } catch (error) {
            productGrid.innerHTML = '<p class="col-span-full text-center p-8 text-red-500">Could not load products.</p>';
            console.error('B2B products fetch error:', error);
        }
    }

    function renderProducts(products) {
        if (!products || products.length === 0) {
            productGrid.innerHTML = '<p class="col-span-full text-center p-8 text-gray-500">No products match your criteria.</p>';
            return;
        }

        const userDiscount = b2bCartManager.getDiscount();

        productGrid.innerHTML = products.map(p => {
            const finalPrice = b2bCartManager.calculatePrice(p.price);
            const hasDiscount = finalPrice < p.price;

            let priceHtml = `<p class="text-lg font-bold text-gray-900">€${finalPrice.toFixed(2)}</p>`;
            if (hasDiscount) {
                priceHtml += `<p class="text-sm text-gray-500 line-through">€${p.price.toFixed(2)}</p>`;
            }

            return `
                <div class="group relative bg-white border rounded-lg shadow-sm overflow-hidden flex flex-col">
                    <div class="aspect-h-1 aspect-w-1 w-full bg-gray-200 group-hover:opacity-75 h-64">
                        <img src="${p.image_url || 'https://placehold.co/400x400/eee/333?text=Image'}" alt="${p.name}" class="h-full w-full object-cover object-center">
                    </div>
                    <div class="p-4 flex flex-col flex-grow">
                        <h3 class="text-sm font-semibold text-gray-800">${p.name}</h3>
                        <p class="mt-1 text-sm text-gray-500 flex-grow">${p.collection?.name || p.category?.name || 'N/A'}</p>
                        <div class="mt-4 flex justify-between items-end">
                            <div>${priceHtml}</div>
                            <button class="add-to-cart-btn bg-indigo-600 text-white font-bold py-2 px-3 rounded-md hover:bg-indigo-700 transition-colors text-sm" data-product-id="${p.id}">
                                Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async function populateFilters() {
        try {
            const data = await apiHelper.get('/products/filters-data');
            categoryFilter.innerHTML = '<option value="">All Categories</option>' + data.categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
            collectionFilter.innerHTML = '<option value="">All Collections</option>' + data.collections.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
            specieFilter.innerHTML = '<option value="">All Species</option>' + data.species.map(s => `<option value="${s}">${s}</option>`).join('');
        } catch (error) {
            document.getElementById('filters-container').innerHTML = '<p class="text-xs text-red-500">Could not load filters.</p>';
        }
    }

    let debounceTimer;
    function debouncedHandleFilterChange() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => handleFilterChange(), 300);
    }

    function handleFilterChange() {
        filters.search = searchInput.value;
        filters.category = categoryFilter.value;
        filters.collection = collectionFilter.value;
        filters.specie = specieFilter.value;
        filters.sort_by = sortBy.value;
        fetchProducts();
    }

    // --- Event Listeners ---
    searchInput.addEventListener('input', debouncedHandleFilterChange);
    categoryFilter.addEventListener('change', handleFilterChange);
    collectionFilter.addEventListener('change', handleFilterChange);
    specieFilter.addEventListener('change', handleFilterChange);
    sortBy.addEventListener('change', handleFilterChange);

    productGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('add-to-cart-btn')) {
            const productId = e.target.dataset.productId;
            b2bCartManager.addToCart(productId, 1);
        }
    });

    // --- Initial Load ---
    populateFilters();
    fetchProducts();
});
