<template>
    <div class="container mx-auto py-12 px-4">
        <h1 class="text-4xl font-serif text-center mb-12">Votre Panier</h1>
        <div v-if="cartStore.isLoading" class="text-center">Mise à jour du panier...</div>
        <div v-if="!cartStore.items.length && !cartStore.isLoading" class="text-center py-16">
            <p class="text-gray-500">Votre panier est vide.</p>
            <router-link to="/nos-produits" class="text-brand-burgundy font-semibold mt-4 inline-block">Continuer vos achats</router-link>
        </div>
        <div v-else>
            <div v-for="item in cartStore.items" v-bind:key="item.id" class="flex items-center border-b py-4">
                <img v-bind:src="item.image_url" class="w-24 h-24 object-cover rounded-md mr-4">
                <div class="flex-grow">
                    <h2 class="text-lg font-semibold">{{ item.name }}</h2>
                    <p>{{ formatCurrency(item.price) }}</p>
                </div>
                <div class="flex items-center">
                    <input type="number" v-bind:value="item.quantity" v-on:change="cartStore.updateQuantity(item.product_id, $event.target.value)" class="w-16 p-2 border rounded-md text-center">
                    <button v-on:click="cartStore.removeFromCart(item.product_id)" class="ml-4 text-red-500 hover:text-red-700">Supprimer</button>
                </div>
            </div>
            <div class="text-right mt-8">
                <h2 class="text-2xl font-bold">Total: {{ formatCurrency(cartStore.cartTotal) }}</h2>
                <button class="btn-primary rounded-md py-3 px-8 text-lg mt-4">Passer la commande</button>
            </div>
        </div>
    </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useB2CCartStore } from '../../stores/B2CCart.js';

export default defineComponent({
    name: 'ShoppingCart',
    setup() {
        const cartStore = useB2CCartStore();

        onMounted(() => {
            cartStore.fetchCart();
        });
        
        const formatCurrency = (value) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);

        return { cartStore, formatCurrency };
    }
});
</script>
