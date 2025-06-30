<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="close">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
      <div class="mt-3 text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Manage Discounts for {{ user.user_email }}</h3>
        <div class="mt-2 px-7 py-3">
          
          <!-- Tier Assignment Form -->
          <form @submit.prevent="submitTierAssignment" class="mb-6">
            <h4 class="text-md font-semibold text-gray-800 mb-2">Assign Tier</h4>
            <div class="flex items-center space-x-4">
              <select v-model="selectedTierId" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                <option :value="null">No Tier</option>
                <option v-for="tier in tiers" :key="tier.id" :value="tier.id">{{ tier.name }} ({{ tier.discount_percentage }}%)</option>
              </select>
              <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">Assign Tier</button>
            </div>
             <p v-if="user.tier_override" class="text-sm text-yellow-600 mt-2">This user has a manual override active.</p>
             <p v-if="user.tier_name" class="text-sm text-gray-600 mt-2">Currently assigned: <strong>{{ user.tier_name }}</strong></p>
          </form>

          <!-- Custom Discount Form -->
          <form @submit.prevent="submitCustomDiscount">
            <h4 class="text-md font-semibold text-gray-800 mb-2">Set Custom Discount</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="discount" class="block text-sm font-medium text-gray-700 text-left">Discount %</label>
                <input type="number" step="0.01" id="discount" v-model="customDiscount.discount" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" placeholder="e.g., 15.5">
              </div>
              <div>
                <label for="limit" class="block text-sm font-medium text-gray-700 text-left">Monthly Spend Limit (€)</label>
                <input type="number" step="0.01" id="limit" v-model="customDiscount.limit" class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" placeholder="e.g., 500">
              </div>
            </div>
             <p class="text-sm text-gray-600 mt-2">Current Spend: <strong>€{{ user.current_monthly_spend || '0.00' }}</strong></p>
             <p v-if="user.custom_discount_percentage" class="text-sm text-gray-600 mt-1">Current Custom Discount: <strong>{{ user.custom_discount_percentage }}%</strong> with a limit of <strong>€{{ user.monthly_spend_limit }}</strong></p>

            <div class="items-center px-4 py-3 mt-4">
                <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700">Set Custom Discount</button>
            </div>
          </form>
        </div>

        <div class="items-center px-4 py-3">
          <button @click="close" class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-600">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAdminUsersStore } from '@/stores/adminUsers';

const props = defineProps({
  show: Boolean,
  user: Object,
  tiers: Array,
});

const emit = defineEmits(['close']);

const adminUsersStore = useAdminUsersStore();

const selectedTierId = ref(null);
const customDiscount = ref({
  discount: 0,
  limit: 0,
});

watch(() => props.user, (newUser) => {
  if (newUser) {
    selectedTierId.value = newUser.tier_id || null;
    customDiscount.value.discount = newUser.custom_discount_percentage || 0;
    customDiscount.value.limit = newUser.monthly_spend_limit || 0;
  }
}, { immediate: true });


const submitTierAssignment = () => {
    if (props.user?.user_id && selectedTierId.value !== null) {
        adminUsersStore.assignTierToUser(props.user.user_id, selectedTierId.value);
    }
};

const submitCustomDiscount = () => {
    if (props.user?.user_id) {
        adminUsersStore.setCustomDiscountForUser(props.user.user_id, customDiscount.value);
    }
};

const close = () => {
  emit('close');
};
</script>
