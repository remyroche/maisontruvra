<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-900">Manage Delivery Options</h1>
    <p class="mt-1 text-sm text-gray-600">Configure which countries you deliver to and the available methods for each.</p>

    <div v-if="isLoading" class="mt-8 text-center">
      <p>Loading settings...</p>
    </div>

    <div v-else class="mt-8">
      <div class="space-y-8">
        <div v-for="country in countries" :key="country.id" class="bg-white p-4 shadow rounded-lg">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">{{ country.name }} ({{ country.code }})</h3>
            <div class="flex items-center space-x-4">
              <label :for="`active-${country.id}`" class="text-sm font-medium text-gray-700">Active</label>
              <input
                type="checkbox"
                :id="`active-${country.id}`"
                v-model="country.is_active"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
            </div>
          </div>
          <div class="mt-4 border-t border-gray-200 pt-4">
            <h4 class="text-sm font-medium text-gray-700">Available Delivery Methods</h4>
            <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <div v-for="option in deliveryOptions" :key="option.id" class="flex items-center">
                <input
                  :id="`country-${country.id}-option-${option.id}`"
                  type="checkbox"
                  :value="option.id"
                  v-model="country.delivery_option_ids"
                  class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <label :for="`country-${country.id}-option-${option.id}`" class="ml-3 text-sm text-gray-600">
                  {{ option.name }} - ${{ option.price }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 text-right">
        <button
          @click="saveSettings"
          :disabled="isSaving"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:bg-gray-400"
        >
          {{ isSaving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

const isLoading = ref(true);
const isSaving = ref(false);
const countries = ref([]);
const deliveryOptions = ref([]);
const notificationStore = useNotificationStore();

onMounted(async () => {
  try {
    const response = await api.adminGetDeliverySettings();
    countries.value = response.data.countries;
    deliveryOptions.value = response.data.delivery_options;
  } catch (error) {
    notificationStore.showNotification('Failed to load delivery settings.', 'error');
  } finally {
    isLoading.value = false;
  }
});

const saveSettings = async () => {
  isSaving.value = true;
  try {
    await api.adminUpdateDeliverySettings({ countries: countries.value });
    notificationStore.showNotification('Delivery settings saved successfully.', 'success');
  } catch (error) {
    notificationStore.showNotification('Failed to save settings.', 'error');
  } finally {
    isSaving.value = false;
  }
};
</script>