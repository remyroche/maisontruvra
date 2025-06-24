<!--
 * FILENAME: website/js/admin/components/CategoryForm.vue
 * DESCRIPTION: A form for creating or editing product category details.
-->
<template>
  <form @submit.prevent="$emit('submit', formData)">
    <div class="space-y-4">
      <div>
        <label for="cat-name" class="block text-sm font-medium text-gray-700">Category Name</label>
        <input type="text" id="cat-name" v-model="formData.name" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>
      <div>
        <label for="cat-desc" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea id="cat-desc" v-model="formData.description" rows="3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
      </div>
    </div>
    <div class="mt-6 flex justify-end space-x-3">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
      <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Save</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  initialData: Object,
});

const emit = defineEmits(['submit', 'cancel']);

const formData = ref({ ...props.initialData });

watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true, immediate: true });
</script>
