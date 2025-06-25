<template>
  <div class="product-form-container">
    <h2>{{ isEditing ? 'Edit Product' : 'Create New Product' }}</h2>
    <Form :validation-schema="schema" :initial-values="product" @submit="handleSubmit" v-slot="{ isSubmitting }">
      <div class="form-group">
        <label for="name">Product Name</label>
        <Field name="name" type="text" id="name" class="form-input" />
        <ErrorMessage name="name" class="error-message" />
      </div>
      
      <div class="form-group">
        <label for="description">Description</label>
        <Field as="textarea" name="description" id="description" class="form-input" rows="4" />
        <ErrorMessage name="description" class="error-message" />
      </div>

      <div class="form-group">
        <label for="price">Price (€)</label>
        <Field name="price" type="number" id="price" class="form-input" step="0.01" />
        <ErrorMessage name="price" class="error-message" />
      </div>

      <div class="form-group">
        <label for="stock_quantity">Stock Quantity</label>
        <Field name="stock_quantity" type="number" id="stock_quantity" class="form-input" />
        <ErrorMessage name="stock_quantity" class="error-message" />
      </div>

      <div class="form-group">
        <label for="is_published">
          <Field name="is_published" type="checkbox" id="is_published" :value="true" />
          Publish this product
        </label>
      </div>

      <button type="submit" class="submit-button" :disabled="isSubmitting">
        <span v-if="isSubmitting">Saving...</span>
        <span v-else>{{ isEditing ? 'Update Product' : 'Create Product' }}</span>
      </button>
    </Form>
  </div>
</template>

<script setup>
import { Form, Field, ErrorMessage } from 'vee-validate';
import { required, isPositiveNumber, isNonNegativeInteger } from '@/validation/rules';

const props = defineProps({
  product: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      price: '',
      stock_quantity: '',
      is_published: false,
    }),
  },
  isEditing: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['submit']);

const schema = {
  name: (value) => required(value),
  description: (value) => required(value),
  price: (value) => required(value) && isPositiveNumber(value),
  stock_quantity: (value) => required(value) && isNonNegativeInteger(value),
};

const handleSubmit = (values) => {
  emit('submit', values);
};
</script>
