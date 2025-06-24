<!--
 * FILENAME: website/js/admin/components/CollectionForm.vue
 * DESCRIPTION: New form component for creating or editing product collections.
-->
<template>
  <form @submit.prevent="$emit('submit', formData)">
    <div class="space-y-4">
      <div>
        <label for="collection-name" class="block text-sm font-medium text-gray-700">Collection Name</label>
        <input type="text" id="collection-name" v-model="formData.name" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
      </div>
      <div>
        <label for="collection-desc" class="block text-sm font-medium text-gray-700">Description</label>
        <textarea id="collection-desc" v-model="formData.description" rows="3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500"></textarea>
      </div>
       <div>
        <label class="flex items-center">
            <input type="checkbox" v-model="formData.is_active" class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
            <span class="ml-2 text-sm text-gray-900">Collection is Active</span>
        </label>
      </div>
    </div>
    <div class="mt-6 flex justify-end space-x-3">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
      <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">Save Collection</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ name: '', description: '', is_active: true })
  }
});

defineEmits(['submit', 'cancel']);

const formData = ref({ ...props.initialData });

watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true, immediate: true });
</script>
