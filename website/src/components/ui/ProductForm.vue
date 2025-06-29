<!-- website/src/components/ui/ProductForm.vue -->
<!-- Description: This component is updated to include client-side validation using VeeValidate and Yup. -->
<template>
  <!-- The Form component from VeeValidate now wraps the form -->
  <Form @submit="handleSubmit" :validation-schema="schema" v-slot="{ errors, isSubmitting }">
    <div class="space-y-6">
      <!-- Product Name Field -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">Product Name</label>
        <Field name="name" type="text" id="name" v-model="localProduct.name"
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
               :class="{ 'border-red-500': errors.name }" />
        <ErrorMessage name="name" class="mt-2 text-sm text-red-600" />
      </div>

      <!-- Product SKU Field -->
      <div>
        <label for="sku" class="block text-sm font-medium text-gray-700">SKU</label>
        <Field name="sku" type="text" id="sku" v-model="localProduct.sku"
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
               :class="{ 'border-red-500': errors.sku }" />
        <ErrorMessage name="sku" class="mt-2 text-sm text-red-600" />
      </div>

      <!-- Price and Stock Fields (in a grid) -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <label for="price" class="block text-sm font-medium text-gray-700">Price (€)</label>
          <Field name="price" type="number" id="price" v-model.number="localProduct.price"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                 :class="{ 'border-red-500': errors.price }"
                 step="0.01" />
          <ErrorMessage name="price" class="mt-2 text-sm text-red-600" />
        </div>
        <div>
          <label for="stock_quantity" class="block text-sm font-medium text-gray-700">Stock Quantity</label>
          <Field name="stock_quantity" type="number" id="stock_quantity" v-model.number="localProduct.stock_quantity"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                 :class="{ 'border-red-500': errors.stock_quantity }" />
          <ErrorMessage name="stock_quantity" class="mt-2 text-sm text-red-600" />
        </div>
      </div>
      
       <!-- Category Selection -->
      <div>
          <label for="category_id" class="block text-sm font-medium text-gray-700">Category</label>
          <Field name="category_id" as="select" id="category_id" v-model="localProduct.category_id"
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                 :class="{ 'border-red-500': errors.category_id }">
              <option value="" disabled>Select a category</option>
              <!-- You would populate this from a store or prop -->
              <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
              </option>
          </Field>
          <ErrorMessage name="category_id" class="mt-2 text-sm text-red-600" />
      </div>

      <!-- Description Field -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
        <Field name="description" as="textarea" id="description" v-model="localProduct.description" rows="4"
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
               :class="{ 'border-red-500': errors.description }"/>
        <ErrorMessage name="description" class="mt-2 text-sm text-red-600" />
      </div>
    </div>

    <div class="mt-8 flex justify-end">
      <button type="button" @click="$emit('cancel')"
              class="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
        Cancel
      </button>
      <button type="submit" :disabled="isSubmitting"
              class="ml-3 inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50">
        {{ isSubmitting ? 'Saving...' : 'Save Product' }}
      </button>
    </div>
  </Form>
</template>

<script setup>
import { ref, watch } from 'vue';
// --- START: Recommendations Implementation ---
import { Form, Field, ErrorMessage } from 'vee-validate';
import * as yup from 'yup';
// --- END: Recommendations Implementation ---

const props = defineProps({
  product: {
    type: Object,
    default: () => ({
      name: '',
      sku: '',
      price: 0,
      stock_quantity: 0,
      category_id: null,
      description: '',
    }),
  },
  // Example categories, in a real app this would come from a Pinia store
  categories: {
      type: Array,
      default: () => [
          { id: 1, name: 'Scented Candles' },
          { id: 2, name: 'Home Fragrance' },
          { id: 3, name: 'Artisanal Soaps' }
      ]
  }
});

const emit = defineEmits(['submit', 'cancel']);

const localProduct = ref({ ...props.product });

// Watch for changes in the product prop to update the local state
watch(() => props.product, (newVal) => {
  localProduct.value = { ...newVal };
}, { deep: true });

// --- START: Recommendations Implementation ---
// Define the validation schema using Yup
const schema = yup.object({
  name: yup.string().required('Product name is required').max(255),
  sku: yup.string().required('SKU is required').max(100),
  price: yup.number().typeError('Price must be a number').required('Price is required').min(0, 'Price cannot be negative'),
  stock_quantity: yup.number().typeError('Stock must be a number').required('Stock quantity is required').integer('Stock must be a whole number').min(0, 'Stock cannot be negative'),
  category_id: yup.number().required('A category must be selected'),
  description: yup.string().notRequired(),
});
// --- END: Recommendations Implementation ---

// The handleSubmit function is called by VeeValidate on successful validation
const handleSubmit = (values) => {
  // `values` is the validated form data from VeeValidate
  emit('submit', values);
};
</script>