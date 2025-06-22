<template>
    <div class="container mx-auto py-12 px-4">
        <h1 class="text-4xl font-serif text-center mb-12">Nos Produits</h1>
        
        <div class="flex justify-center mb-8 space-x-4">
            <button v-on:click="productStore.fetchProducts()" class="font-semibold text-gray-700 hover:text-brand-burgundy">Tous</button>
            <button v-for="category in productStore.categories" v-bind:key="category.slug" v-on:click="productStore.fetchProducts(category.slug)" class="font-semibold text-gray-700 hover:text-brand-burgundy">
                {{ category.name }}
            </button>
        </div>

        <div v-if="productStore.isLoading" class="text-center text-gray-500">Chargement des produits...</div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div v-for="product in productStore.products" v-bind:key="product.id" class="card-hover bg-white rounded-lg shadow-lg overflow-hidden">
                <a v-bind:href="`/produit/${product.slug}`">
                    <img v-bind:src="product.image_url" v-bind:alt="product.name" class="w-full h-64 object-cover">
                    <div class="p-6">
                        <h2 class="text-xl font-serif text-brand-burgundy">{{ product.name }}</h2>
                        <p class="text-lg font-semibold mt-2">{{ formatCurrency(product.price) }}</p>
                    </div>
                </a>
                 <div class="px-6 pb-4">
                    <button v-on:click="cartStore.addToCart(product.id, 1)" class="w-full btn-primary rounded-md py-2">
                        Ajouter au Panier
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useProductStore } from '../../stores/product.js';
import { useCartStore } from '../../stores/cart.js';

export default defineComponent({
    name: 'ProductCatalogue',
    setup() {
        const productStore = useProductStore();
        const cartStore = useCartStore();

        onMounted(() => {
            productStore.fetchProducts();
            productStore.fetchCategories();
        });

        const formatCurrency = (value) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);

        return {
            productStore,
            cartStore,
            formatCurrency
        };
    }
});
</script>
