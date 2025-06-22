// website/source/js/stores/product.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '../api-client.js';

export const useProductStore = defineStore('product', () => {
    // STATE
    const products = ref([]);
    const currentProduct = ref(null);
    const categories = ref([]);
    const isLoading = ref(false);

    // ACTIONS
    async function fetchProducts(categorySlug = null) {
        isLoading.value = true;
        try {
            const endpoint = categorySlug ? `/products?category=${categorySlug}` : '/products';
            const data = await apiClient.get(endpoint);
            products.value = data.products;
        } catch (error) {
            console.error("Failed to fetch products:", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchProductBySlug(slug) {
        isLoading.value = true;
        currentProduct.value = null;
        try {
            const data = await apiClient.get(`/products/${slug}`);
            currentProduct.value = data;
        } catch (error) {
            console.error(`Failed to fetch product ${slug}:`, error);
        } finally {
            isLoading.value = false;
        }
    }
    
    async function fetchCategories() {
        try {
            const data = await apiClient.get('/products/categories');
            categories.value = data.categories;
        } catch (error) {
            console.error("Failed to fetch categories:", error);
        }
    }

    return { products, currentProduct, categories, isLoading, fetchProducts, fetchProductBySlug, fetchCategories };
});
