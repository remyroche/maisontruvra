<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Roles</h1>
    <div v-if="systemStore.error" class="text-red-500">{{ systemStore.error }}</div>
    <div class="mb-4">
        <h2 class="text-xl font-semibold">Create Role</h2>
        <form @submit.prevent="createRole">
            <input v-model="newRole.name" placeholder="Role Name" class="border rounded p-2 mr-2">
            <input v-model="newRole.permissions" placeholder="Permissions (comma-separated)" class="border rounded p-2 mr-2">
            <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded">Create</button>
        </form>
    </div>
    <div>
      <table class="min-w-full bg-white">
        <thead>
          <tr>
            <th class="py-2">Role</th>
            <th class="py-2">Permissions</th>
            <th class="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in systemStore.roles" :key="role.id">
            <td class="border px-4 py-2">{{ role.name }}</td>
            <td class="border px-4 py-2">{{ role.permissions.join(', ') }}</td>
            <td class="border px-4 py-2">
                <button @click="deleteRole(role.id)" class="bg-red-500 text-white px-4 py-2 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import { useAdminSystemStore } from '@/js/stores/adminSystem';

const systemStore = useAdminSystemStore();

const newRole = reactive({
    name: '',
    permissions: ''
});

onMounted(() => {
  systemStore.fetchRoles();
});

const createRole = () => {
    const permissions = newRole.permissions.split(',').map(p => p.trim());
    systemStore.createRole({ name: newRole.name, permissions });
    newRole.name = '';
    newRole.permissions = '';
};

const deleteRole = (roleId) => {
    systemStore.deleteRole(roleId);
};
</script>
