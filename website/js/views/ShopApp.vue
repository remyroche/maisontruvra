<template>
    <div>
        <Notification />
        
        <component :is="currentView" :key="$route.fullPath"></component>
    </div>
</template>

<script>
import { defineComponent, computed } from 'vue';
import { useRoute } from 'vue-router';

// Import components
import ProductCatalogue from './components/shop/ProductCatalogue.vue';
import ProductDetail from './components/shop/ProductDetail.vue';
import ShoppingCart from './components/shop/ShoppingCart.vue';
import UserProfile from './components/shop/UserProfile.vue';
import Notification from './components/ui/Notification.vue';

const routes = {
    '/nos-produits': ProductCatalogue,
    '/produit': ProductDetail, // Assumes a slug will be in the query, e.g., /produit?slug=...
    '/panier': ShoppingCart,
    '/compte': UserProfile
};

export default defineComponent({
    name: 'ShopApp',
    components: {
        ProductCatalogue,
        ProductDetail,
        ShoppingCart,
        UserProfile,
        Notification
    },
    setup() {
        const route = useRoute();
        const currentView = computed(() => {
            // Very simple router logic
            // For product detail, we check for a specific path part
            if (route.path.startsWith('/produit/')) {
                return ProductDetail;
            }
            return routes[route.path] || ProductCatalogue; // Default to catalogue
        });

        return {
            currentView,
        };
    }
});
</script>
