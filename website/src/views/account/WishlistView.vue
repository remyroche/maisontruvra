<!-- website/src/views/account/WishlistView.vue -->
<template>
  <div>
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Ma Liste d'Envies</h1>
    
    <div v-if="isLoading" class="mt-8 text-center">
      <p class="text-gray-500">Chargement de votre liste d'envies...</p>
    </div>

    <div v-else-if="error" class="mt-8 text-center p-6 bg-red-50 rounded-lg">
        <p class="text-red-700">{{ error }}</p>
    </div>
    
    <div v-else-if="!wishlistItems || wishlistItems.length === 0" class="mt-8 text-center py-12 px-6 bg-gray-50 rounded-lg">
      <p class="text-lg font-medium text-gray-900">Votre liste d'envies est vide.</p>
      <p class="mt-2 text-sm text-gray-500">Parcourez nos collections pour trouver des produits qui vous plaisent.</p>
      <router-link to="/shop" class="mt-6 inline-block rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700">
        Découvrir les produits
      </router-link>
    </div>

    <div v-else class="mt-8 grid grid-cols-1 gap-y-10 gap-x-6 sm:grid-cols-2 lg:grid-cols-3 xl:gap-x-8">
      <div v-for="item in wishlistItems" :key="item.id" class="group relative flex flex-col">
        <div class="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-md bg-gray-200 group-hover:opacity-75">
          <img :src="item.product_image_url || 'https://placehold.co/400x400/F4E9E2/7C3242?text=Image'" :alt="item.product_name" class="h-full w-full object-cover object-center" />
        </div>
        <div class="mt-4 flex justify-between">
          <div>
            <h3 class="text-sm text-gray-700">
              <router-link :to="{ name: 'ProductDetail', params: { id: item.product_id } }">
                <span aria-hidden="true" class="absolute inset-0" />
                {{ item.product_name }}
              </router-link>
            </h3>
          </div>
          <p class="text-sm font-medium text-gray-900">{{ formatCurrency(item.product_price) }}</p>
        </div>
        <div class="mt-4 flex flex-1 items-end space-x-2">
            <button @click="handleAddToCart(item)" class="flex-1 rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
                Ajouter au panier
            </button>
            <button @click="handleRemoveFromWishlist(item.product_id)" class="rounded-md border border-gray-300 bg-white p-2 text-gray-400 hover:bg-gray-50 hover:text-red-500">
                <TrashIcon class="h-5 w-5" />
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { useCartStore } from '@/stores/cart';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { TrashIcon } from '@heroicons/vue/24/outline';

const userStore = useUserStore();
const cartStore = useCartStore();
const { formatCurrency } = useCurrencyFormatter();

const isLoading = ref(true);
const error = ref(null);

// Use a computed property to reactively get wishlist items from the store
const wishlistItems = computed(() => userStore.wishlist);

const fetchWishlist = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // This action should fetch items and populate the store's state
    await userStore.fetchWishlist();
  } catch (err) {
    console.error("Failed to fetch wishlist:", err);
    error.value = "Impossible de charger votre liste d'envies.";
  } finally {
    isLoading.value = false;
  }
};

const handleAddToCart = (wishlistItem) => {
    const product = {
        id: wishlistItem.product_id,
        name: wishlistItem.product_name,
        price: wishlistItem.product_price,
        image_url: wishlistItem.product_image_url
    };
    cartStore.addItem({ product, quantity: 1 });
    // Also remove from wishlist after adding to cart
    handleRemoveFromWishlist(wishlistItem.product_id);
};

const handleRemoveFromWishlist = async (productId) => {
    try {
        await userStore.removeFromWishlist(productId);
        // The list will update automatically because it's a computed property
    } catch (err) {
        console.error("Failed to remove item from wishlist:", err);
        // Optionally show an error notification
    }
};

onMounted(() => {
  fetchWishlist();
});
</script>
