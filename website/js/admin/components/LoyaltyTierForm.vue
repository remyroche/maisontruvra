<template>
  <form @submit.prevent="submit" class="space-y-4">
    <div>
      <label class="block text-sm font-medium">Tier Name</label>
      <input v-model="form.name" type="text" required class="mt-1 block w-full border p-2 rounded">
    </div>
    <div>
      <label class="block text-sm font-medium">Minimum Points</label>
      <input v-model.number="form.min_points" type="number" required class="mt-1 block w-full border p-2 rounded">
    </div>
    <div>
      <label class="block text-sm font-medium">Points Multiplier (e.g., 1.5)</label>
      <input v-model.number="form.multiplier" type="number" step="0.1" required class="mt-1 block w-full border p-2 rounded">
    </div>
    <button type="submit" class="bg-indigo-600 text-white w-full py-2 rounded">Save Tier</button>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  tier: Object,
});
const emit = defineEmits(['save']);

const form = ref({ name: '', min_points: 0, multiplier: 1.0 });

watch(() => props.tier, (newVal) => {
    if (newVal) {
        form.value = { ...newVal };
    }
}, { immediate: true, deep: true });

const submit = () => {
  emit('save', form.value);
};
</script>
