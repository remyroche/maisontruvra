<template>
  <Modal :is-open="isOpen" @close="cancel">
    <div class="p-2">
      <div class="flex items-start">
        <div class="flex-shrink-0 mx-auto flex items-center justify-center h-12 w-12 rounded-full" :class="`bg-${color}-100`">
          <!-- Heroicon name: exclamation / check / etc. -->
          <svg :class="`h-6 w-6 text-${color}-600`" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="ml-4 text-left">
          <h3 class="text-lg leading-6 font-medium text-gray-900">{{ title }}</h3>
          <div class="mt-2">
            <p class="text-sm text-gray-600">{{ message }}</p>
          </div>
        </div>
      </div>
      <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
        <button 
          @click="confirm" 
          type="button" 
          class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white sm:ml-3 sm:w-auto sm:text-sm"
          :class="`bg-${color}-600 hover:bg-${color}-700 focus:ring-${color}-500`"
        >
          Confirm
        </button>
        <button 
          @click="cancel" 
          type="button" 
          class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
        >
          Cancel
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import Modal from './Modal.vue';

defineProps({
  isOpen: { type: Boolean, required: true },
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, required: true },
  color: { type: String, default: 'danger' } // e.g., danger, warning, primary
});

const emit = defineEmits(['confirm', 'cancel']);

const confirm = () => emit('confirm');
const cancel = () => emit('cancel');
</script>
