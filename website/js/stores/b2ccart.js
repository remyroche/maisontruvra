// website/source/js/stores/b2ccart.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '../api-client.js';
import { useNotificationStore } from './notification.js';

export const useCartStore = defineStore('cart', () => {
    // STATE
    const items = ref([]);
    const isLoading = ref(false);

    // GETTERS
    const cartCount = computed(() => items.value.reduce((acc, item) => acc + item.quantity, 0));
    const cartTotal = computed(() => items.value.reduce((acc, item) => acc + (item.price * item.quantity), 0));

    // ACTIONS
    async function fetchCart() {
        isLoading.value = true;
        try {
            const data = await apiClient.get('/cart');
            items.value = data.items || [];
        } catch (error) {
            console.error("Failed to fetch cart:", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function addToCart(productId, quantity = 1) {
        isLoading.value = true;
        const notificationStore = useNotificationStore();
        try {
            const data = await apiClient.post('/cart/add', { product_id: productId, quantity });
            items.value = data.items;
            notificationStore.showNotification('Product added to cart!', 'success');
        } catch (error) {
            notificationStore.showNotification('Could not add product to cart.', 'error');
        } finally {
            isLoading.value = false;
        }
    }

    async function updateQuantity(productId, quantity) {
        if (quantity <= 0) {
            return await removeFromCart(productId);
        }
        isLoading.value = true;
        try {
            const data = await apiClient.put('/cart/update', { product_id: productId, quantity });
            items.value = data.items;
        } catch (error) {
            console.error("Failed to update item quantity:", error);
        } finally {
            isLoading.value = false;
        }
    }
    
    async function removeFromCart(productId) {
        isLoading.value = true;
        try {
            const data = await apiClient.post('/cart/remove', { product_id: productId });
            items.value = data.items;
        } catch (error) {
            console.error("Failed to remove item from cart:", error);
        } finally {
            isLoading.value = false;
        }
    }

    return { items, isLoading, cartCount, cartTotal, fetchCart, addToCart, updateQuantity, removeFromCart };
});
