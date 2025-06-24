<!--
 * FILENAME: website/js/admin/components/BlogArticleForm.vue
 * DESCRIPTION: New form for creating/editing blog articles.
-->
<template>
  <form @submit.prevent="$emit('submit', formData)">
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium">Title</label>
        <input type="text" v-model="formData.title" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
      </div>
       <div>
        <label class="block text-sm font-medium">Category</label>
        <select v-model="formData.category_id" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            <option :value="null">-- Select Category --</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium">Content</label>
        <textarea v-model="formData.content" rows="10" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
      </div>
       <div>
        <label class="flex items-center">
            <input type="checkbox" v-model="formData.is_published" class="h-4 w-4 text-indigo-600 rounded">
            <span class="ml-2 text-sm">Published</span>
        </label>
      </div>
    </div>
    <div class="mt-6 flex justify-end space-x-3">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
      <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Save Article</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';
const props = defineProps({
  initialData: Object,
  categories: Array
});
defineEmits(['submit', 'cancel']);
const formData = ref({ ...props.initialData });
watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true, immediate: true });
</script>
