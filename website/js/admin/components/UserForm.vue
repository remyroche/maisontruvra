<!--
 * FILENAME: website/js/admin/components/UserForm.vue
 * DESCRIPTION: A form for creating or editing user details.
 *
 * This component contains all the input fields required to manage a user's data.
 * It's designed to be used within a modal. It takes an optional `initialData` prop
 * to populate the form for editing, and emits a `submit` event with the form
 * data when the user saves changes.
-->
<template>
  <form @submit.prevent="handleSubmit">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Email Field -->
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
        <input type="email" id="email" v-model="formData.email" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
      </div>
      
      <!-- Role Field -->
      <div>
        <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
        <select id="role" v-model="formData.role" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          <option>user</option>
          <option>admin</option>
          <option>b2b_user</option>
        </select>
      </div>
      
      <!-- First Name Field -->
      <div>
        <label for="first_name" class="block text-sm font-medium text-gray-700">First Name</label>
        <input type="text" id="first_name" v-model="formData.first_name" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
      </div>
      
      <!-- Last Name Field -->
      <div>
        <label for="last_name" class="block text-sm font-medium text-gray-700">Last Name</label>
        <input type="text" id="last_name" v-model="formData.last_name" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
      </div>

      <!-- Verified Checkbox -->
       <div class="col-span-1 md:col-span-2">
        <label class="flex items-center">
            <input type="checkbox" v-model="formData.is_verified" class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
            <span class="ml-2 text-sm text-gray-900">Is Verified</span>
        </label>
      </div>

    </div>
    
    <!-- Form Actions -->
    <div class="mt-6 flex justify-end">
      <button type="button" @click="$emit('cancel')" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded mr-2">
        Cancel
      </button>
      <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">
        {{ isEditing ? 'Update User' : 'Create User' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ email: '', first_name: '', last_name: '', role: 'user', is_verified: false })
  }
});

const emit = defineEmits(['submit', 'cancel']);

const formData = ref({ ...props.initialData });
const isEditing = computed(() => !!props.initialData.id);

// Watch for changes in initialData to reset the form when a new user is selected for editing
watch(() => props.initialData, (newData) => {
  formData.value = { ...newData };
}, { deep: true });

const handleSubmit = () => {
  // Deep copy the form data to avoid reactivity issues
  const submissionData = JSON.parse(JSON.stringify(formData.value));
  emit('submit', submissionData);
};
</script>
