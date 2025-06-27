<template>
  <form @submit.prevent="handleSubmit">
    <div class="space-y-4">
      <div>
        <label for="referral_count" class="block text-sm font-medium text-gray-700">Referral Count</label>
        <input type="number" id="referral_count" v-model="form.referral_count" min="1" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" required>
      </div>
      <div>
        <label for="reward_description" class="block text-sm font-medium text-gray-700">Reward Description</label>
        <textarea id="reward_description" v-model="form.reward_description" rows="3" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" required></textarea>
      </div>
    </div>
    <div class="mt-6">
      <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        Save Reward
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  tier: {
    type: Object,
    default: () => ({ referral_count: 1, reward_description: '' })
  }
});

const emit = defineEmits(['save']);

const form = ref({ ...props.tier });

watch(() => props.tier, (newTier) => {
  form.value = { ...newTier };
});

const handleSubmit = () => {
  emit('save', { ...form.value });
};
</script>
