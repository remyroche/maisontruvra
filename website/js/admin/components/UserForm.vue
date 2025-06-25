<template>
  <form @submit.prevent="submitForm" class="space-y-4">
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
      <input type="email" id="email" v-model="form.email" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
    </div>

    <div>
      <label for="password" class="block text-sm font-medium text-gray-700">Password (leave blank to keep unchanged)</label>
      <input type="password" id="password" v-model="form.password" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
    </div>

    <div>
      <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
      <select id="role" v-model="form.role_id" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
        <option v-for="role in systemStore.roles" :key="role.id" :value="role.id">{{ role.name }}</option>
      </select>
    </div>
    
    <div class="flex items-center">
      <input id="is-active" type="checkbox" v-model="form.is_active" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
      <label for="is-active" class="ml-2 block text-sm text-gray-900">Active</label>
    </div>

     <div class="flex items-center">
      <input id="is-frozen" type="checkbox" v-model="form.is_frozen" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
      <label for="is-frozen" class="ml-2 block text-sm text-gray-900">Frozen</label>
    </div>

    <div class="flex justify-end space-x-4">
        <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300">Cancel</button>
        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Save</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAdminSystemStore } from '@/js/stores/adminSystem';

const props = defineProps({
  user: {
    type: Object,
    default: () => ({ email: '', password: '', role_id: null, is_active: true, is_frozen: false })
  }
});

const emit = defineEmits(['save', 'cancel']);

const systemStore = useAdminSystemStore();

const form = ref({ ...props.user });

watch(() => props.user, (newUser) => {
  form.value = { ...newUser };
});

onMounted(() => {
    systemStore.fetchRoles();
});

const submitForm = () => {
    // Make sure to not send an empty password if it's not being changed
    const dataToSend = { ...form.value };
    if (!dataToSend.password) {
        delete dataToSend.password;
    }
  emit('save', dataToSend);
};
</script>
