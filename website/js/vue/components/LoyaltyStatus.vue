<template>
    <section id="loyalty" class="py-16">
        <div class="container mx-auto px-4">
            <div v-if="loyaltyStore.isLoading" class="text-center text-gray-500">Chargement de l'Atelier Privé...</div>
            <div v-else>
                 <h2 class="font-serif text-4xl text-brand-dark-brown mb-12 text-center">Votre Atelier Privé</h2>
                 <div class="grid md:grid-cols-3 gap-8 mb-16">
                    <div class="md:col-span-2 bg-white p-8 rounded-lg shadow-lg border-l-4 border-brand-gold card-hover">
                        <h3 class="font-serif text-2xl text-brand-dark-brown">Votre Statut</h3>
                        <p class="font-sans text-brand-dark-gray mb-4">Vous êtes actuellement <strong class="text-brand-burgundy">{{ loyaltyStore.status.tier_name }}</strong>.</p>
                        <div class="w-full bg-gray-200 rounded-full h-4 mb-2"><div class="bg-brand-gold h-4 rounded-full" v-bind:style="{ width: loyaltyStore.status.progress_percentage + '%' }"></div></div>
                        <p class="text-sm text-brand-dark-gray text-right">{{ loyaltyStore.status.next_tier_message }}</p>
                    </div>
                    <div class="bg-brand-dark-brown text-white p-8 rounded-lg shadow-lg text-center flex flex-col justify-center card-hover">
                        <h3 class="font-sans font-bold uppercase tracking-wider mb-2">Points Valides</h3>
                        <p class="font-serif text-5xl">{{ loyaltyStore.status.points }}</p>
                    </div>
                </div>
                <!-- Le reste de la section fidélité et parrainage ici -->
            </div>
        </div>
    </section>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useLoyaltyStore } from '../../stores/loyalty.js';

export default defineComponent({
    name: 'LoyaltyStatus',
    setup() {
        const loyaltyStore = useLoyaltyStore();

        onMounted(() => {
            if (!loyaltyStore.status.tier_name) { // Ne recharge que si les données ne sont pas déjà là
                loyaltyStore.fetchLoyaltyData();
            }
        });

        return {
            loyaltyStore,
        };
    }
});
</script>
