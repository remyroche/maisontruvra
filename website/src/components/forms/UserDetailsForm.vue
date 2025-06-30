<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
      <div>
        <label for="firstName" class="block text-sm font-medium leading-6 text-gray-900">Prénom</label>
        <div class="mt-2">
          <input type="text" id="firstName" v-model="form.firstName" @input="emitUpdate"
                 class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                 required autocomplete="given-name">
        </div>
      </div>
      <div>
        <label for="lastName" class="block text-sm font-medium leading-6 text-gray-900">Nom</label>
        <div class="mt-2">
          <input type="text" id="lastName" v-model="form.lastName" @input="emitUpdate"
                 class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                 required autocomplete="family-name">
        </div>
      </div>
    </div>
    <div class="sm:col-span-2">
      <label for="email" class="block text-sm font-medium leading-6 text-gray-900">Email</label>
      <div class="mt-2">
        <input type="email" id="email" v-model="form.email" @input="emitUpdate"
               class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
               required autocomplete="email">
      </div>
    </div>
    <div v-if="includePassword" class="sm:col-span-2">
      <label for="password" class="block text-sm font-medium leading-6 text-gray-900">Mot de passe</label>
      <div class="mt-2">
        <input type="password" id="password" v-model="form.password" @input="emitUpdate"
               class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
               required autocomplete="new-password">
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';

// This component uses v-model for two-way data binding.
// It accepts an object with user details and emits updates.

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({ firstName: '', lastName: '', email: '', password: '' })
  },
  includePassword: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

// Local reactive form state, initialized from props
const form = reactive({ ...props.modelValue });

// Watch for changes in the prop to update the local state.
// This is useful if the parent component resets the form.
watch(() => props.modelValue, (newValue) => {
  Object.assign(form, newValue);
}, { deep: true });

// Emit an update event whenever any input changes.
const emitUpdate = () => {
  emit('update:modelValue', { ...form });
};
</script>
