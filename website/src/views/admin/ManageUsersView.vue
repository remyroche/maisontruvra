<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6">Manage Users</h1>
    
    <div v-if="store.isLoading" class="text-center">
      <p>Loading users...</p>
    </div>
    
    <div v-else-if="store.error" class="text-red-500 text-center">
      <p>{{ store.error }}</p>
    </div>

    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tier</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Custom Discount</th>
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in store.users" :key="user.user_id">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ user.user_email }}</div>
                <div v-if="user.company_name" class="text-sm text-gray-500">{{ user.company_name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.user_id ? 'B2B' : 'B2C' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.tier_name || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.custom_discount_percentage ? `${user.custom_discount_percentage}%` : 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="openDiscountModal(user)" class="text-indigo-600 hover:text-indigo-900">Manage Discounts</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <UserDiscountModal 
      :show="isModalOpen" 
      :user="selectedUser"
      :tiers="store.tiers"
      @close="closeDiscountModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminUsersStore } from '@/stores/adminUsers';
import UserDiscountModal from '@/components/admin/UserDiscountModal.vue';

const store = useAdminUsersStore();
const isModalOpen = ref(false);
const selectedUser = ref(null);

onMounted(() => {
  store.fetchUsers();
  store.fetchTiers();
});

const openDiscountModal = (user) => {
  selectedUser.value = user;
  isModalOpen.value = true;
};

const closeDiscountModal = () => {
  isModalOpen.value = false;
  selectedUser.value = null;
};
</script>
