<template>
    <form @submit.prevent="submit" class="space-y-2">
        <input v-model="form.name" placeholder="New category name" required class="w-full border p-2 rounded">
        <textarea v-model="form.description" placeholder="Description (optional)" rows="2" class="w-full border p-2 rounded"></textarea>
        <button type="submit" class="bg-blue-500 text-white w-full py-2 rounded">Add Category</button>
    </form>
</template>

<script setup>
import { ref } from 'vue';

const emit = defineEmits(['save']);

const form = ref({ name: '', description: '' });

const submit = () => {
    emit('save', form.value);
    form.value = { name: '', description: '' }; // Reset form
};
</script>
