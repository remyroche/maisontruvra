<template>
    <section class="py-16">
        <div class="container mx-auto px-4">
             <div v-if="loading" class="text-center text-gray-500">Chargement des statistiques...</div>
             <div v-else class="grid md:grid-cols-3 gap-8">
                 <div class="bg-white p-8 rounded-lg shadow-lg text-center border-t-4 border-brand-gold card-hover">
                     <h3 class="font-serif font-bold tracking-wider mb-2 text-brand-dark-gray">Dépenses Totales</h3>
                     <p class="font-serif text-5xl text-brand-burgundy">{{ formatCurrency(stats.total_spend) }}</p>
                </div>
                 <div class="bg-white p-8 rounded-lg shadow-lg text-center border-t-4 border-brand-gold card-hover">
                     <h3 class="font-serif font-bold tracking-wider mb-2 text-brand-dark-gray">Commandes Totales</h3>
                     <p class="font-serif text-5xl text-brand-burgundy">{{ stats.total_orders }}</p>
                </div>
                <div class="bg-white p-8 rounded-lg shadow-lg text-center border-t-4 border-brand-gold card-hover">
                     <h3 class="font-serif font-bold tracking-wider mb-2 text-brand-dark-gray">Panier Moyen</h3>
                     <p class="font-serif text-5xl text-brand-burgundy">{{ formatCurrency(stats.average_order_value) }}</p>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import { apiClient } from '../../api-client.js';

export default defineComponent({
    name: 'DashboardStats',
    setup() {
        const loading = ref(true);
        const stats = ref({});

        const formatCurrency = (value) => {
            return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);
        };

        onMounted(async () => {
            try {
                stats.value = await apiClient.get('/b2b/dashboard/statistics');
            } catch (error) {
                console.error("Impossible de charger les statistiques du tableau de bord.", error);
            } finally {
                loading.value = false;
            }
        });

        return {
            loading,
            stats,
            formatCurrency,
        };
    }
});
</script>
