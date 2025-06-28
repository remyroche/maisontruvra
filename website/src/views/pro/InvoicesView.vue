<template>
  <div class="container mx-auto py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Invoices</h1>

    <div v-if="isLoading" class="text-center py-12">
      <p>Loading invoices...</p>
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
      <p>Could not load your invoices. Please try again later.</p>
    </div>

    <div v-else-if="invoices && invoices.items.length > 0">
      <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice #</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th scope="col" class="relative px-6 py-3"><span class="sr-only">Download</span></th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="invoice in invoices.items" :key="invoice.id">
              <td class="px-6 py-4 whitespace-nowrap">{{ invoice.invoice_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap">{{ new Date(invoice.issue_date).toLocaleDateString() }}</td>
              <td class="px-6 py-4 whitespace-nowrap">€{{ invoice.total_amount.toFixed(2) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="statusClass(invoice.status)">
                  {{ invoice.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a v-if="invoice.pdf_download_url" :href="invoice.pdf_download_url" target="_blank" class="text-indigo-600 hover:text-indigo-900">Download</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Add Pagination Controls Here -->
    </div>

    <div v-else class="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
      <h3 class="text-lg font-medium text-gray-900">No Invoices Found</h3>
      <p class="mt-1 text-sm text-gray-500">You do not have any invoices yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApiData } from '@/composables/useApiData';
import { apiClient } from '@/services/api'; // Assuming B2B uses the standard client

const currentPage = ref(1);
const invoicesPerPage = ref(10);

const { data: invoices, isLoading, error } = useApiData(
  () => apiClient.get(`/b2b/profile/invoices?page=${currentPage.value}&per_page=${invoicesPerPage.value}`),
  () => currentPage.value // Re-fetch when page changes
);

const statusClass = (status) => {
  const lowerStatus = status.toLowerCase();
  if (lowerStatus === 'paid') return 'bg-green-100 text-green-800';
  if (lowerStatus === 'pending') return 'bg-yellow-100 text-yellow-800';
  if (lowerStatus === 'overdue') return 'bg-red-100 text-red-800';
  return 'bg-gray-100 text-gray-800';
};
</script>