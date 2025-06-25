<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Site Settings</h1>
    <div v-if="settingsStore.isLoading">Loading settings...</div>
    <form v-else @submit.prevent="save" class="bg-white p-6 rounded-lg shadow space-y-4 max-w-2xl">
        <div v-for="(value, key) in form" :key="key">
            <label :for="key" class="block text-sm font-medium text-gray-700">{{ formatKey(key) }}</label>
            <input v-if="typeof value === 'boolean'" type="checkbox" :id="key" v-model="form[key]" class="mt-1 h-4 w-4 rounded">
            <input v-else-if="typeof value === 'number'" type="number" :id="key" v-model.number="form[key]" class="mt-1 block w-full border p-2 rounded">
            <input v-else type="text" :id="key" v-model="form[key]" class="mt-1 block w-full border p-2 rounded">
        </div>
        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded">Save Settings</button>
    </form>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAdminSiteSettingsStore } from '@/js/stores/adminSiteSettings';

const settingsStore = useAdminSiteSettingsStore();
const form = ref({});

onMounted(() => settingsStore.fetchSettings());

watch(() => settingsStore.settings, (newVal) => {
    form.value = { ...newVal };
}, { deep: true });

const save = async () => {
    await settingsStore.saveSettings(form.value);
    alert('Settings saved!');
};
const formatKey = (key) => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
</script>
