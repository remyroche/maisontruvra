<template>
    <main>
        <!-- B2B Dashboard Section -->
        <section id="dashboard" class="hero-section text-cream py-20 md:py-24 bg-truffle-burgundy">
             <div class="container mx-auto px-4 text-center">
                <h2 class="text-4xl font-serif text-gold mb-4">Welcome to your Portal</h2>
                <p class="text-lg">Here's a summary of your activity.</p>
            </div>
        </section>
        <section class="py-16">
            <div v-if="store.dashboard.isLoading" class="text-center py-16">Chargement du tableau de bord...</div>
            <div v-if="store.dashboard.error" class="text-center py-16 text-red-600">Erreur de chargement.</div>
            <div v-if="!store.dashboard.isLoading && !store.dashboard.error && store.dashboard.kpis" class="container mx-auto px-4">
                <!-- Example of how you might display KPIs -->
                 <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="bg-cream p-6 rounded-lg shadow-md text-center">
                        <h4 class="text-lg font-serif text-dark-brown">Total Spent</h4>
                        <p class="text-3xl font-bold text-truffle-burgundy mt-2">{{ formatCurrency(store.dashboard.kpis.total_spent) }}</p>
                    </div>
                    <div class="bg-cream p-6 rounded-lg shadow-md text-center">
                        <h4 class="text-lg font-serif text-dark-brown">Orders Placed</h4>
                        <p class="text-3xl font-bold text-truffle-burgundy mt-2">{{ store.dashboard.kpis.orders_placed }}</p>
                    </div>
                     <div class="bg-cream p-6 rounded-lg shadow-md text-center">
                        <h4 class="text-lg font-serif text-dark-brown">Loyalty Points</h4>
                        <p class="text-3xl font-bold text-truffle-burgundy mt-2">{{ store.loyalty.data.points || '0' }}</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Divider -->
        <div class="container mx-auto my-16"><div class="border-t border-gray-200"></div></div>

        <!-- B2B Loyalty Section -->
        <section id="loyalty" class="py-16">
            <div v-if="store.loyalty.isLoading" class="text-center py-16">Chargement de l'atelier...</div>
            <div v-if="store.loyalty.error" class="text-center py-16 text-red-600">Erreur de chargement.</div>
             <div v-if="!store.loyalty.isLoading && !store.loyalty.error && store.loyalty.data" class="container mx-auto px-4">
                 <h2 class="font-serif text-4xl text-dark-brown mb-12 text-center">Your Loyalty Tier</h2>
                 <div class="bg-gold text-dark-brown p-8 rounded-lg shadow-lg text-center">
                    <h3 class="text-3xl font-serif">Current Tier: {{ store.loyalty.data.tier_name }}</h3>
                    <p class="mt-4">You have {{ store.loyalty.data.points }} points.</p>
                 </div>
             </div>
        </section>

        <!-- Divider -->
        <div class="container mx-auto my-16"><div class="border-t border-gray-200"></div></div>
        
        <!-- B2B Invoices Section -->
        <section id="invoices" class="py-16">
            <div v-if="store.invoices.isLoading" class="text-center py-16">Chargement des factures...</div>
            <div v-if="store.invoices.error" class="text-center py-16 text-red-600">Erreur de chargement.</div>
            <div v-if="!store.invoices.isLoading && !store.invoices.error" class="container mx-auto px-4">
                <h2 class="font-serif text-4xl text-dark-brown mb-12 text-center">Recent Invoices</h2>
                <div class="bg-white overflow-hidden rounded-lg shadow-lg">
                    <table class="min-w-full">
                        <thead class="bg-cream border-b-2 border-gold">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-dark-brown uppercase tracking-wider">Invoice ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-dark-brown uppercase tracking-wider">Date</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-dark-brown uppercase tracking-wider">Total</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-dark-brown uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-right text-xs font-medium text-dark-brown uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            <tr v-for="invoice in store.invoices.list.slice(0, 5)" :key="invoice.id">
                                 <td class="px-6 py-4 whitespace-nowrap">{{ invoice.id }}</td>
                                 <td class="px-6 py-4 whitespace-nowrap">{{ new Date(invoice.created_at).toLocaleDateString() }}</td>
                                 <td class="px-6 py-4 whitespace-nowrap">{{ formatCurrency(invoice.total) }}</td>
                                 <td class="px-6 py-4 whitespace-nowrap">
                                    <span :class="getStatusClass(invoice.status)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                                        {{ invoice.status }}
                                    </span>
                                 </td>
                                 <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <a :href="`/api/b2b/invoices/${invoice.id}`" class="text-truffle-burgundy hover:text-gold">Download</a>
                                 </td>
                            </tr>
                        </tbody>
                    </table>
                     <div class="p-4 text-center" v-if="store.invoices.list.length > 5">
                        <router-link to="/pro/invoices-pro" class="text-truffle-burgundy hover:text-gold font-semibold">View All Invoices</router-link>
                    </div>
                </div>
             </div>
        </section>
    </main>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useB2BPortalStore } from '../stores/b2b-portal';

const store = useB2BPortalStore();

onMounted(() => {
    // Fetch all data needed for the portal when the component mounts
    store.fetchDashboardData();
    store.fetchLoyaltyData();
    store.fetchInvoices();
    store.fetchProfileData();
});


const formatCurrency = (value) => {
  if (typeof value !== 'number') return '';
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value);
};

const getStatusClass = (status) => {
    if (status === 'PAID') return 'bg-green-100 text-green-800';
    if (status === 'PENDING') return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
};
</script>
