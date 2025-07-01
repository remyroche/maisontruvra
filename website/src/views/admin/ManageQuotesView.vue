<template>
  <div class="p-6">
    <h1 class="text-2xl font-semibold mb-4">Manage Quote Requests</h1>
    <div class="bg-white shadow rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quote ID</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th scope="col" class="relative px-6 py-3"><span class="sr-only">Respond</span></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="quote in quotes" :key="quote.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ quote.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ quote.user.company_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="statusClass(quote.status)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                {{ quote.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(quote.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link :to="{ name: 'AdminRespondToQuote', params: { id: quote.id } }" class="text-brand-burgundy hover:text-brand-dark-brown">
                View / Respond
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useB2BStore } from '@/stores/b2b';
import { useDateFormatter } from '@/composables/useDateFormatter';

const b2bStore = useB2BStore();
const { formatDate } = useDateFormatter();
const quotes = ref([]);

onMounted(async () => {
  await b2bStore.fetchQuotes();
  quotes.value = b2bStore.quotes;
});

const statusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    accepted: 'bg-green-100 text-green-800',
    responded: 'bg-blue-100 text-blue-800',
    expired: 'bg-gray-100 text-gray-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};
</script>
