// website/src/stores/products.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';

export const useProductStore = defineStore('product', () => {
    // --- STATE ---
    const products = ref([]); // For product listings
    const currentProduct = ref(null);
    const loading = ref(false);
    const error = ref(null);

    // --- NEW STATE for Recently Viewed ---
    const recentlyViewedIds = ref(JSON.parse(localStorage.getItem('recentlyViewed') || '[]'));
    const recentlyViewedProducts = ref([]);
    const recentlyViewedLoading = ref(false);

    // --- GETTERS ---
    const recentlyViewed = computed(() => recentlyViewedProducts.value);

    // --- ACTIONS ---
    async function fetchAllProducts() {
        loading.value = true;
        error.value = null;
        try {
            const response = await api.get('/products'); // Assuming a public endpoint
            products.value = response.data;
        } catch (err) {
            error.value = 'Failed to fetch products.';
            console.error(err);
        } finally {
            loading.value = false;
        }
    }

    async function fetchProductById(productId) {
        loading.value = true;
        error.value = null;
        currentProduct.value = null;
        try {
            const response = await api.get(`/products/${productId}`);
            currentProduct.value = response.data;
            // --- ADD TO RECENTLY VIEWED ---
            addProductToRecentlyViewed(productId);
            return response.data;
        } catch (err) {
            error.value = 'Failed to fetch product details.';
            console.error(err);
            throw err;
        } finally {
            loading.value = false;
        }
    }

    // --- NEW ACTIONS for Recently Viewed ---
    function addProductToRecentlyViewed(productId) {
        if (!productId) return;

        // Remove the id if it already exists to move it to the front
        const index = recentlyViewedIds.value.indexOf(productId);
        if (index > -1) {
            recentlyViewedIds.value.splice(index, 1);
        }

        // Add the new id to the beginning of the array
        recentlyViewedIds.value.unshift(productId);

        // Keep the list at a reasonable size (e.g., 5 items)
        if (recentlyViewedIds.value.length > 5) {
            recentlyViewedIds.value.pop();
        }

        // Persist to localStorage
        localStorage.setItem('recentlyViewed', JSON.stringify(recentlyViewedIds.value));
    }

    async function fetchRecentlyViewedProducts() {
        if (recentlyViewedIds.value.length === 0) {
            recentlyViewedProducts.value = [];
            return;
        }
        
        recentlyViewedLoading.value = true;
        try {
            // Assuming a new backend endpoint that can fetch multiple products by their IDs
            // POST /api/products/batch with a body of { ids: [1, 2, 3] }
            const response = await api.post('/products/batch', { ids: recentlyViewedIds.value });
            // The backend should return products in the same order as the IDs requested.
            recentlyViewedProducts.value = response.data;
        } catch (err) {
            console.error('Failed to fetch recently viewed products:', err);
            // Don't show a user-facing error, just log it.
        } finally {
            recentlyViewedLoading.value = false;
        }
    }

    return {
        products,
        currentProduct,
        loading,
        error,
        recentlyViewed,
        recentlyViewedLoading,
        fetchAllProducts,
        fetchProductById,
        fetchRecentlyViewedProducts,
    };
});