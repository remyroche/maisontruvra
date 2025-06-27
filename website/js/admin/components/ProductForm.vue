<template>
  <Form @submit="handleSubmit" :validation-schema="productSchema" :initial-values="product" v-slot="{ errors }">
    <!-- ... existing form fields for name, price, sku, etc. ... -->
    
    <div class="mt-4">
      <label for="internal_note" class="block text-sm font-medium text-gray-700">Internal Note</label>
      <Field name="internal_note" as="textarea" id="internal_note" rows="3"
             class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm" />
    </div>

    <div class="mt-6 border-t pt-6">
      <h3 class="text-lg font-medium text-gray-900">Visibility Rules</h3>
      <div class="mt-4 space-y-4">
        <div class="flex items-start">
          <div class="flex items-center h-5">
            <Field name="is_b2c_visible" type="checkbox" :value="true" id="is_b2c_visible" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded" />
          </div>
          <div class="ml-3 text-sm">
            <label for="is_b2c_visible" class="font-medium text-gray-700">Visible to B2C Customers</label>
          </div>
        </div>
         <div class="flex items-start">
          <div class="flex items-center h-5">
            <Field name="is_b2b_visible" type="checkbox" :value="true" id="is_b2b_visible" class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded" />
          </div>
          <div class="ml-3 text-sm">
            <label for="is_b2b_visible" class="font-medium text-gray-700">Visible to B2B Customers</label>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-700">Restrict to Specific Loyalty Tiers (Optional)</label>
      <p class="text-xs text-gray-500">If none are selected, the product is visible to all (based on B2C/B2B flags). If one or more are selected, it's *only* visible to members of those tiers.</p>
      <div class="mt-2 space-y-2">
        <div v-for="tier in loyaltyStore.tiers" :key="tier.id" class="flex items-center">
            <Field name="restricted_to_tier_ids" type="checkbox" :value="tier.id" :id="`tier_${tier.id}`"
                   class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded" />
            <label :for="`tier_${tier.id}`" class="ml-3 block text-sm font-medium text-gray-700">{{ tier.name }}</label>
        </div>
      </div>
    </div>

    <div class="mt-8">
      <button type="submit" class="w-full btn-primary">Save Product</button>
    </div>
  </Form>
</template>

<script setup>
import { onMounted } from 'vue';
import { Form, Field } from 'vee-validate';
import * as yup from 'yup';
import { useAdminLoyaltyStore } from '../../stores/adminLoyalty';

const props = defineProps({
  product: Object,
});
const emit = defineEmits(['save']);

const loyaltyStore = useAdminLoyaltyStore();

const productSchema = yup.object({
  // ... validation for other fields
  name: yup.string().required(),
  price: yup.number().required().positive(),
  stock: yup.number().required().integer().min(0),
  internal_note: yup.string().optional(),
  is_b2c_visible: yup.boolean(),
  is_b2b_visible: yup.boolean(),
  restricted_to_tier_ids: yup.array().of(yup.string()),
});

onMounted(() => {
    loyaltyStore.fetchLoyaltyTiers();
});

function handleSubmit(values) {
  emit('save', values);
}
</script>
