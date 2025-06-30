<template>
  <!-- This component has been refactored to use the generic ui/Modal.vue -->
  <Modal :is-open="isOpen" @close="closeModal">
    <template #default>
      <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
        <div class="sm:flex sm:items-start">
          <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 sm:mx-0 sm:h-10 sm:w-10">
            <!-- Heroicon name: gift -->
            <svg class="h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1014.625 7.5H9.375A2.625 2.625 0 1012 4.875zM21 11.25H3v1.875h18v-1.875z" />
            </svg>
          </div>
          <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
            <h3 class="text-base font-semibold leading-6 text-gray-900" id="modal-title">
              Assign Discount to {{ user.email }}
            </h3>
            <div class="mt-4 space-y-4">
              <div>
                <label for="discount-code" class="block text-sm font-medium text-gray-700">Discount Code</label>
                <input type="text" v-model="discountCode" id="discount-code" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              </div>
              <div>
                <label for="discount-value" class="block text-sm font-medium text-gray-700">Percentage</label>
                <input type="number" v-model.number="discountValue" id="discount-value" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
        <button @click="handleAssign" type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto">
          Assign
        </button>
        <button @click="closeModal" type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto">
          Cancel
        </button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref } from 'vue';
import Modal from '@/components/ui/Modal.vue';
import { useAdminUsersStore } from '@/stores/adminUsers';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps({
  isOpen: { type: Boolean, required: true },
  user: { type: Object, required: true }
});

const emit = defineEmits(['close']);

const adminUsersStore = useAdminUsersStore();
const notificationStore = useNotificationStore();
const discountCode = ref('');
const discountValue = ref(10);

const closeModal = () => {
  emit('close');
};

const handleAssign = async () => {
  if (!discountCode.value || discountValue.value <= 0) {
    notificationStore.addNotification('Please provide a valid code and percentage.', 'error');
    return;
  }
  try {
    await adminUsersStore.assignDiscountToUser({
      userId: props.user.id,
      code: discountCode.value,
      percentage: discountValue.value,
    });
    notificationStore.addNotification('Discount assigned successfully.', 'success');
    closeModal();
  } catch (error) {
    notificationStore.addNotification(error.message || 'Failed to assign discount.', 'error');
  }
};
</script>
