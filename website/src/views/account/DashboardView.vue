<!-- website/src/views/account/DashboardView.vue -->
<template>
  <div>
    <h1 class="text-3xl font-bold tracking-tight text-gray-900">Mon Compte</h1>
    <p class="mt-2 text-sm text-gray-600">Bienvenue, {{ userStore.user?.first_name || 'client' }}. D'ici, vous pouvez consulter vos commandes récentes et gérer vos informations personnelles.</p>

    <div class="mt-8">
      <h2 class="text-xl font-semibold text-gray-900">Commandes Récentes</h2>

      <div v-if="orderStore.loading" class="mt-4 text-center">
        <p class="text-gray-500">Chargement des commandes...</p>
      </div>
      <div v-else-if="orderStore.error" class="mt-4 text-center text-red-500">
        {{ orderStore.error }}
      </div>
      <div v-else-if="orders.length === 0" class="mt-4 text-center bg-gray-50 p-8 rounded-lg">
        <p class="text-gray-600">Vous n'avez pas encore passé de commande.</p>
        <router-link to="/shop" class="mt-4 inline-block text-indigo-600 hover:text-indigo-800 font-medium">
          Commencer vos achats &rarr;
        </router-link>
      </div>
      
      <!-- Orders List -->
      <div v-else class="mt-4 flow-root">
        <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <table class="min-w-full divide-y divide-gray-300">
              <thead>
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">N° Commande</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Date</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Statut</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Total</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                    <span class="sr-only">View</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50 cursor-pointer" @click="viewOrder(order.id)">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">#{{ order.id }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatDate(order.created_at) }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium" :class="statusClass(order.order_status)">
                      {{ order.order_status }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatCurrency(order.total_price) }}</td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                    <router-link :to="{ name: 'OrderStatus', params: { id: order.id } }" class="text-indigo-600 hover:text-indigo-900">
                      Voir<span class="sr-only">, order #{{ order.id }}</span>
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useOrderStore } from '@/stores/orders';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';
import { useDateFormatter } from '@/composables/useDateFormatter';

const userStore = useUserStore();
const orderStore = useOrderStore();
const router = useRouter();
const { formatCurrency } = useCurrencyFormatter();
const { formatDate } = useDateFormatter();

const orders = computed(() => orderStore.orders);

const viewOrder = (orderId) => {
  router.push({ name: 'OrderStatus', params: { id: orderId } });
};

const statusClass = (status) => {
  switch (status) {
    case 'Delivered':
      return 'bg-green-100 text-green-800';
    case 'Shipped':
      return 'bg-blue-100 text-blue-800';
    case 'Cancelled':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-yellow-100 text-yellow-800';
  }
};

onMounted(() => {
  orderStore.fetchUserOrders();
});
</script>
