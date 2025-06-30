<template>
  <div class="bg-gray-50 min-h-screen py-8">
    <div class="container mx-auto px-4">
      <h1 class="text-2xl font-semibold mb-4">Shopping Cart</h1>
      <div class="flex flex-col md:flex-row gap-4">
        
        <!-- Cart Items Section -->
        <div class="md:w-3/4">
          <div class="bg-white rounded-lg shadow-md p-6 mb-4">
            
            <!-- Loading State -->
            <div v-if="cartStore.loading" class="text-center py-10">
              <p class="text-gray-500">Loading cart items...</p>
            </div>

            <!-- Empty Cart State -->
            <div v-else-if="!cartStore.items.length" class="text-center py-10">
              <p class="text-gray-500">Your cart is empty.</p>
              <router-link to="/shop" class="text-blue-500 hover:underline mt-2 inline-block">Continue Shopping</router-link>
            </div>
            
            <!-- Cart Items List -->
            <table v-else class="w-full">
              <thead>
                <tr>
                  <th class="text-left font-semibold">Product</th>
                  <th class="text-left font-semibold">Price</th>
                  <th class="text-left font-semibold">Quantity</th>
                  <th class="text-left font-semibold">Total</th>
                  <th class="text-left font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in cartStore.items" :key="item.id" class="border-b">
                  <td class="py-4">
                    <div class="flex items-center">
                      <img class="h-16 w-16 mr-4 rounded" :src="item.product.image_url || 'https://placehold.co/64x64/eee/ccc?text=IMG'" :alt="item.product.name">
                      <span class="font-semibold">{{ item.product.name }}</span>
                    </div>
                  </td>
                  <td class="py-4">${{ item.product.price.toFixed(2) }}</td>
                  <td class="py-4">
                    <div class="flex items-center">
                      <input type="number" class="w-16 text-center border rounded" :value="item.quantity" @change="updateItemQuantity(item.id, $event.target.value)">
                    </div>
                  </td>
                  <td class="py-4 font-semibold">${{ (item.product.price * item.quantity).toFixed(2) }}</td>
                  <td class="py-4">
                    <button @click="cartStore.removeFromCart(item.id)" class="text-red-500 hover:text-red-700">
                      Remove
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Order Summary Section -->
        <div class="md:w-1/4">
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-lg font-semibold mb-4">Order Summary</h2>
            <div class="flex justify-between mb-2">
              <span>Subtotal ({{ cartStore.itemCount }} items)</span>
              <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between mb-2">
              <span>Taxes</span>
              <span>TBD</span>
            </div>
            <div class="flex justify-between mb-2">
              <span>Shipping</span>
              <span>TBD</span>
            </div>
            <hr class="my-2">
            <div class="flex justify-between font-semibold">
              <span>Total</span>
              <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
            </div>
            <button class="bg-blue-500 text-white py-2 px-4 rounded-lg mt-4 w-full hover:bg-blue-600" :disabled="!cartStore.items.length">
              Proceed to Checkout
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useCartStore } from '@/stores/cart';

// 1. Instantiate the cart store to access its state, getters, and actions.
const cartStore = useCartStore();

// 2. Fetch cart data from the backend when the component is first mounted.
//    This ensures the user sees their most up-to-date cart.
onMounted(() => {
  cartStore.fetchCart();
});

/**
 * Handles the logic for updating an item's quantity.
 * @param {number} itemId - The ID of the cart item to update.
 * @param {string} quantityStr - The new quantity from the input field.
 */
function updateItemQuantity(itemId, quantityStr) {
    const quantity = parseInt(quantityStr, 10);
    if (!isNaN(quantity)) {
        cartStore.updateQuantity(itemId, quantity);
    }
}
</script>
