<template>
  <form @submit.prevent="submitForm" class="p-4">
    <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit' : 'Add' }} Category</h2>
    <div class="mb-4">
      <label for="name" class="block text-sm font-medium text-gray-700">Category Name</label>
      <input type="text" id="name" v-model="form.name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
    </div>
    <div class="mb-4">
      <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
      <textarea id="description" v-model="form.description" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
    </div>
    <div class="flex justify-end space-x-2">
      <button type="button" @click="$emit('cancel')" class="px-4 py-2 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300">Cancel</button>
      <button type="submit" class="px-4 py-2 rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 border border-transparent">Save</button>
    </div>
  </form>
</template>

<script>
import { ref, watch, computed } from 'vue';

export default {
  name: 'CategoryForm',
  props: {
    category: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const form = ref({});

    const isEditing = computed(() => !!(form.value && form.value.id));

    watch(() => props.category, (newVal) => {
      // Create a copy to avoid mutating the prop directly
      form.value = { ...newVal };
    }, { immediate: true });

    const submitForm = () => {
      emit('save', form.value);
    };

    return {
      form,
      isEditing,
      submitForm,
    };
  },
};
</script>