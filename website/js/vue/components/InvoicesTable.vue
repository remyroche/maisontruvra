<template>
    <section id="invoices" class="py-16">
         <div class="container mx-auto px-4">
            <h2 class="font-serif text-4xl text-brand-dark-brown mb-12 text-center">Historique des Factures</h2>
            <div class="bg-white overflow-hidden rounded-lg shadow-lg">
                <table class="min-w-full">
                    <thead class="bg-brand-burgundy text-white">
                        <tr>
                            <th scope="col" class="py-4 px-6 text-left text-sm font-bold uppercase tracking-wider">N° de Facture</th>
                            <th scope="col" class="py-4 px-6 text-left text-sm font-bold uppercase tracking-wider">Date</th>
                            <th scope="col" class="py-4 px-6 text-right text-sm font-bold uppercase tracking-wider">Total</th>
                            <th scope="col" class="py-4 px-6 text-center text-sm font-bold uppercase tracking-wider">Statut</th>
                            <th scope="col" class="relative py-3.5 px-6"><span class="sr-only">Actions</span></th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        <tr v-if="invoiceStore.isLoading"><td colspan="5" class="p-8 text-center text-gray-500">Chargement des factures...</td></tr>
                        <tr v-else-if="invoiceStore.invoices.length === 0"><td colspan="5" class="p-8 text-center text-gray-500">Aucune facture trouvée.</td></tr>
                        <tr v-for="invoice in invoiceStore.invoices" v-bind:key="invoice.invoice_number">
                            <td class="p-4 text-gray-500">{{ invoice.invoice_number }}</td>
                            <td class="p-4 text-gray-500">{{ formatDate(invoice.date) }}</td>
                            <td class="p-4 text-right">{{ formatCurrency(invoice.total) }}</td>
                            <td class="p-4 text-center">
                                <span class="rounded-full px-3 py-1 text-xs font-semibold" v-bind:class="getInvoiceStatusClass(invoice.status)">
                                    {{ invoice.status }}
                                </span>
                            </td>
                            <td class="p-4 text-right">
                                <a v-bind:href="invoice.download_url" class="font-semibold text-brand-burgundy hover:text-brand-gold transition-colors">Télécharger</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
         </div>
    </section>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import { useInvoiceStore } from '../../stores/invoices.js';

export default defineComponent({
    name: 'InvoicesTable',
    setup() {
        const invoiceStore = useInvoiceStore();
        
        onMounted(() => {
            if (invoiceStore.invoices.length === 0) {
                 invoiceStore.fetchInvoices();
            }
        });

        const formatCurrency = (value) => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);
        const formatDate = (dateString) => new Date(dateString).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
        const getInvoiceStatusClass = (status) => {
            const lowerStatus = status.toLowerCase();
            if (lowerStatus === 'payée') return 'bg-green-100 text-green-800';
            if (lowerStatus === 'en attente') return 'bg-yellow-100 text-yellow-800';
            return 'bg-gray-100 text-gray-800';
        };
        
        return { 
            invoiceStore,
            formatCurrency,
            formatDate,
            getInvoiceStatusClass
        };
    }
});
</script>
