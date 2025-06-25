<template>
  <form @submit.prevent="submit" class="space-y-4">
    <div>
      <label>Title</label>
      <input v-model="form.title" type="text" required class="w-full border p-2 rounded">
    </div>
    <div>
      <label>Content</label>
      <textarea v-model="form.content" rows="10" required class="w-full border p-2 rounded"></textarea>
    </div>
    <div>
      <label>Category</label>
      <select v-model="form.category_id" class="w-full border p-2 rounded">
        <option :value="null">Select a category</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
      </select>
    </div>
    <div>
      <label class="flex items-center">
        <input v-model="form.is_published" type="checkbox" class="mr-2">
        Published
      </label>
    </div>
    <div class="flex justify-end space-x-2">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 px-4 py-2 rounded">Cancel</button>
      <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded">Save</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  article: Object,
  categories: Array,
});
const emit = defineEmits(['save', 'cancel']);

const form = ref({});

watch(() => props.article, (newVal) => {
    form.value = { ...newVal };
}, { immediate: true });

const submit = () => {
  emit('save', form.value);
};
</script>

