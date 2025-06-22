<template>
    <main>
        <!-- Invoices content here, using `store.invoices` properties -->
        <section id="invoices" class="py-16">
             <div class="container mx-auto px-4">
                <h2 class="font-serif text-4xl text-brand-dark-brown mb-12 text-center">Historique des Factures</h2>
                <div v-if="!store.invoices.isLoading" class="bg-white overflow-hidden rounded-lg shadow-lg">
                    <table class="min-w-full">
                        <thead class="bg-brand-cream border-b-2 border-brand-gold">
                            <tr>
                                <th scope="col" class="py-4 px-6 text-left text-sm font-bold text-brand-burgundy uppercase tracking-wider">N° de Facture</th>
                                <th scope="col" class="py-4 px-6 text-left text-sm font-bold text-brand-burgundy uppercase tracking-wider">Date</th>
                                <th scope="col" class="py-4 px-6 text-right text-sm font-bold text-brand-burgundy uppercase tracking-wider">Total</th>
                                <th scope="col" class="py-4 px-6 text-center text-sm font-bold text-brand-burgundy uppercase tracking-wider">Statut</th>
                                <th scope="col" class="relative py-3.5 px-6"><span class="sr-only">Actions</span></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                            <tr v-for="invoice in store.invoices.list" :key="invoice.id">
                                <td class="p-4 text-gray-500">{{ invoice.invoice_number }}</td>
                                <td class="p-4 text-gray-500">{{ formatDate(invoice.date) }}</td>
                                <td class="p-4 text-right">{{ formatPrice(invoice.total) }}</td>
                                <td class="p-4 text-center"><span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusClass(invoice.status)">{{ invoice.status }}</span></td>
                                <td class="p-4 text-right"><a :href="invoice.download_url" class="text-brand-burgundy hover:text-brand-gold">Télécharger</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
             </div>
        </section>
    </main>
</template>

<script setup>
import { onMounted } from 'vue';
import { useB2BPortalStore } from '../stores/b2b-portal';

const store = useB2BPortalStore();

onMounted(() => {
    store.fetchInvoices();
});

const formatPrice = (value) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);
const formatDate = (dateString) => new Date(dateString).toLocaleDateString('fr-FR');
const statusClass = (status) => ({
  'Payée': 'bg-green-100 text-green-800',
  'En attente': 'bg-yellow-100 text-yellow-800',
}[status] || 'bg-gray-100 text-gray-800');
</script>
