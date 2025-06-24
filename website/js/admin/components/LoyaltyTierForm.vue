<!--
 * FILENAME: website/js/admin/components/LoyaltyTierForm.vue
 * DESCRIPTION: New form for creating/editing loyalty tiers.
-->
<template>
    <form @submit.prevent="$emit('submit', formData)">
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium">Tier Name</label>
                <input type="text" v-model="formData.name" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div>
                <label class="block text-sm font-medium">Minimum Spend (€)</label>
                <input type="number" v-model.number="formData.min_spend" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div>
                <label class="block text-sm font-medium">Multiplier (e.g., 1.5 for 1.5x points)</label>
                <input type="number" step="0.1" v-model.number="formData.multiplier" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
            <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
            <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Save Tier</button>
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
