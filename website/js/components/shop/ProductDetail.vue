<template>
    <div class="container mx-auto py-12 px-4">
        <div v-if="productStore.isLoading" class="text-center text-gray-500 py-24">Chargement du produit...</div>
        <div v-else-if="!productStore.currentProduct" class="text-center text-gray-500 py-24">Produit non trouvé.</div>
        <div v-else class="grid md:grid-cols-2 gap-12">
            <div>
                <img v-bind:src="productStore.currentProduct.image_url" v-bind:alt="productStore.currentProduct.name" class="w-full rounded-lg shadow-lg">
            </div>
            <div>
                <h1 class="text-4xl font-serif text-brand-burgundy">{{ productStore.currentProduct.name }}</h1>
                <p class="text-2xl font-semibold my-4">{{ formatCurrency(productStore.currentProduct.price) }}</p>
                <p class="text-gray-600 leading-relaxed">{{ productStore.currentProduct.description }}</p>
                <div class="mt-8">
                    <button v-on:click="cartStore.addToCart(productStore.currentProduct.id, 1)" class="btn-primary rounded-md py-3 px-8 text-lg" v-bind:disabled="cartStore.isLoading">
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
import { useB2CCartStore } from '../../stores/B2CCart.js';

export default defineComponent({
    name: 'ProductDetail',
    props: {
        slug: {
            type: String,
            required: true,
        },
    },
    setup(props) {
        const productStore = useProductStore();
        const cartStore = useB2CCartStore();

        onMounted(() => {
            productStore.fetchProductBySlug(props.slug);
        });

        const formatCurrency = (value) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);

        return {
            productStore,
            cartStore,
            formatCurrency,
        };
    },
});
</script>
