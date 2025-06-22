<template>
    <div class="container mx-auto py-12 px-4">
        <h1 class="text-4xl font-serif text-center mb-12">Mon Compte</h1>
        <div v-if="userStore.isLoading" class="text-center">Chargement de votre profil...</div>
        <div v-else-if="userStore.profile">
            <div class="bg-white p-8 rounded-lg shadow-md max-w-2xl mx-auto">
                <h2 class="text-2xl font-serif mb-4">Bonjour, {{ userStore.profile.first_name }}</h2>
                <p><strong>Email:</strong> {{ userStore.profile.email }}</p>
                
                <h3 class="text-xl font-serif mt-8 border-t pt-6">Historique des commandes</h3>
                 <div v-if="!userStore.orders.length" class="text-gray-500 mt-4">Vous n'avez pas encore passé de commande.</div>
                 <div v-else>
                    <!-- Boucle sur les commandes ici -->
                 </div>
            </div>
        </div>
    </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useUserStore } from '../../stores/user.js';

export default defineComponent({
    name: 'UserProfile',
    setup() {
        const userStore = useUserStore();

        onMounted(() => {
            userStore.fetchProfile();
            userStore.fetchOrders();
        });
        
        return { userStore };
    }
});
</script>
