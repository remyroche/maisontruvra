<!--
 * FILENAME: website/js/admin/components/BlogCategoryForm.vue
 * DESCRIPTION: New form for creating/editing blog categories.
-->
<template>
    <form @submit.prevent="$emit('submit', formData)">
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium">Category Name</label>
                <input type="text" v-model="formData.name" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
            <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
            <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Save Category</button>
        </div>
    </form>
</template>

<script setup>
import { ref, watch } from 'vue';
const props = defineProps({ initialData: Object });
defineEmits(['submit', 'cancel']);
const formData = ref({ ...props.initialData });
watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true, immediate: true });
</script>
