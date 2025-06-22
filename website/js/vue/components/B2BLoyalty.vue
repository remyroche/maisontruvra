<template>
    <main>
        <!-- Loyalty content here, using `store.loyalty` properties -->
        <section id="loyalty" class="py-16">
            <div class="container mx-auto px-4">
                 <h2 class="font-serif text-4xl text-brand-dark-brown mb-12 text-center">Votre Atelier Privé</h2>
                 <div v-if="!store.loyalty.isLoading" class="grid md:grid-cols-3 gap-8 mb-16">
                    <div class="md:col-span-2 bg-white p-8 rounded-lg shadow-lg">
                        <h3 class="font-serif text-2xl text-brand-dark-brown">Votre Statut</h3>
                        <p class="font-sans text-brand-dark-gray mb-4">Vous êtes actuellement <strong class="text-brand-burgundy">{{ store.loyalty.tier }}</strong>.</p>
                        <div class="w-full bg-gray-200 rounded-full h-4 mb-2"><div class="bg-brand-gold h-4 rounded-full" :style="{width: store.loyalty.rank_percentage + '%'}"></div></div>
                        <p class="text-sm text-brand-dark-gray text-right">Atteignez le top {{ store.loyalty.next_tier_percentage }}% pour devenir <strong class="text-brand-burgundy">{{ store.loyalty.next_tier }}</strong>.</p>
                    </div>
                    <div class="bg-brand-cream border border-brand-gold p-8 rounded-lg shadow-lg text-center flex flex-col justify-center">
                        <h3 class="font-sans font-bold uppercase tracking-wider mb-2 text-brand-dark-brown">Points Valides</h3>
                        <p class="font-serif text-5xl text-brand-dark-brown">{{ store.loyalty.points_balance }}</p>
                    </div>
                </div>
                <!-- Other loyalty sections -->
            </div>
        </section>
    </main>
</template>

<script setup>
import { onMounted } from 'vue';
import { useB2BPortalStore } from '../stores/b2b-portal';

const store = useB2BPortalStore();

onMounted(() => {
    store.fetchLoyaltyData();
});
</script>
