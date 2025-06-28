<!--
 * FILENAME: website/src/components/ui/Modal.vue
 * DESCRIPTION: A reusable modal/dialog component.
 *
 * This component provides a generic modal overlay. It uses Vue slots to allow
 * any content (like a form or a confirmation message) to be placed inside it.
 * It handles the open/close logic and emits an event when closed.
-->
<template>
  <transition name="modal-fade">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60" @click.self="close">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg mx-auto m-8 max-h-[90vh] overflow-y-auto" role="dialog" aria-modal="true">
        <!-- Modal Header -->
        <header v-if="$slots.header" class="flex items-center justify-between p-4 border-b">
          <slot name="header">
            <h2 class="text-xl font-bold text-gray-800">Modal Title</h2>
          </slot>
          <button @click="close" class="text-gray-500 hover:text-gray-800 text-2xl leading-none" aria-label="Close modal">&times;</button>
        </header>

        <!-- Modal Body -->
        <section class="p-6">
          <slot>
            <p>This is the modal body.</p>
          </slot>
        </section>

        <!-- Modal Footer -->
        <footer v-if="$slots.footer" class="flex justify-end p-4 bg-gray-50 border-t">
          <slot name="footer">
            <button @click="close" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">
              Close
            </button>
          </slot>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
</style>
