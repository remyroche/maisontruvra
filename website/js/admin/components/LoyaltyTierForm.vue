<template>
  <Form @submit="handleSubmit" :validation-schema="loyaltyTierSchema" :initial-values="form" v-slot="{ errors }">
    <div class="space-y-4">
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">Tier Name</label>
        <Field name="name" type="text" id="name" v-model="form.name"
               class="mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none sm:text-sm"
               :class="{'border-red-500': errors.name, 'border-gray-300': !errors.name}" />
        <ErrorMessage name="name" class="text-red-500 text-sm mt-1" />
      </div>

      <div>
        <label for="min_spend" class="block text-sm font-medium text-gray-700">Minimum Spend (€)</label>
        <Field name="min_spend" type="number" id="min_spend" v-model="form.min_spend"
               class="mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none sm:text-sm"
               :class="{'border-red-500': errors.min_spend, 'border-gray-300': !errors.min_spend}" />
        <ErrorMessage name="min_spend" class="text-red-500 text-sm mt-1" />
      </div>

      <div>
        <label for="points_per_euro" class="block text-sm font-medium text-gray-700">Points per Euro</label>
        <Field name="points_per_euro" type="number" step="0.1" id="points_per_euro" v-model="form.points_per_euro"
               class="mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none sm:text-sm"
               :class="{'border-red-500': errors.points_per_euro, 'border-gray-300': !errors.points_per_euro}" />
        <ErrorMessage name="points_per_euro" class="text-red-500 text-sm mt-1" />
      </div>

      <div>
        <label for="benefits" class="block text-sm font-medium text-gray-700">Benefits (comma-separated)</label>
        <Field name="benefits" as="textarea" id="benefits" v-model="form.benefits" rows="3"
               class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none sm:text-sm" />
      </div>
    </div>
    <div class="mt-6">
      <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        Save Tier
      </button>
    </div>
  </Form>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Form, Field, ErrorMessage } from 'vee-validate';
import { loyaltyTierSchema } from '../../validation/schemas';

const props = defineProps({
  tier: {
    type: Object,
    default: () => ({ name: '', min_spend: 0, points_per_euro: 1.0, benefits: '' })
  }
});

const emit = defineEmits(['save']);

const form = ref({ ...props.tier });

watch(() => props.tier, (newTier) => {
  form.value = { ...newTier };
}, { deep: true });

const handleSubmit = (values) => {
  emit('save', values);
};
</script>
