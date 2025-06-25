<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Users</h1>
    
    <div class="mb-4 flex justify-between items-center">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search users by email..." 
        class="border rounded p-2 w-1/3"
      >
      <div class="flex items-center space-x-4">
        <label class="flex items-center text-sm">
            <input type="checkbox" v-model="includeDeleted" @change="fetchData" class="mr-2 h-4 w-4 rounded">
            Show Deleted
        </label>
        <button @click="openCreateModal" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
          Create User
        </button>
      </div>
    </div>

    <div v-if="usersStore.isLoading" class="text-center p-4">Loading users...</div>
    <div v-if="usersStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ usersStore.error }}</div>

    <BaseDataTable
      v-if="!usersStore.isLoading && filteredUsers.length"
      :headers="headers"
      :items="filteredUsers"
    >
        <template #row="{ item, children }">
            <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                <td v-for="header in headers" :key="header.value" class="px-6 py-4 whitespace-nowrap text-sm">
                    <slot :name="`item-${header.value}`" :item="item">{{ getNestedValue(item, header.value) }}</slot>
                </td>
            </tr>
        </template>
        
        <template #item-email="{ item }">
            <span>{{ item.email }}</span>
            <span v-if="item.is_deleted" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-200 text-red-800">Deleted</span>
        </template>

        <template #item-actions="{ item }">
            <div class="flex items-center space-x-2">
                <button v-if="!item.is_deleted" @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900 text-sm">Edit</button>
                <button v-if="!item.is_deleted" @click="confirmDelete(item, 'soft')" class="text-yellow-600 hover:text-yellow-900 text-sm">Soft Delete</button>
                <button v-if="item.is_deleted" @click="restoreUser(item.id)" class="text-green-600 hover:text-green-900 text-sm">Restore</button>
                <button v-if="canHardDelete" @click="confirmDelete(item, 'hard')" class="text-red-600 hover:text-red-900 text-sm">Hard Delete</button>
            </div>
        </template>
    </BaseDataTable>
    
    <div v-if="!usersStore.isLoading && !filteredUsers.length" class="text-center text-gray-500 mt-8">
        No users found.
    </div>

    <Modal :is-open="isModalOpen" @close="closeModal">
      <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit User' : 'Create User' }}</h2>
      <UserForm :user="selectedUser" @save="handleSave" @cancel="closeModal"/>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminUsersStore } from '@/js/stores/adminUsers';
import { useAdminAuthStore } from '@/js/stores/adminAuth';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';
import UserForm from '@/js/admin/components/UserForm.vue';

const usersStore = useAdminUsersStore();
const authStore = useAdminAuthStore();

const searchQuery = ref('');
const includeDeleted = ref(false);
const isModalOpen = ref(false);
const isEditing = ref(false);
const selectedUser = ref(null);

const headers = [
  { text: 'Email', value: 'email' },
  { text: 'Role', value: 'role.name' },
  { text: 'Active', value: 'is_active' },
  { text: 'Frozen', value: 'is_frozen' },
  { text: 'Actions', value: 'actions', sortable: false },
];

const canHardDelete = computed(() => {
  if (!authStore.user || !authStore.user.roles) return false;
  const userRoles = authStore.user.roles.map(r => r.name);
  return userRoles.includes('Admin') || userRoles.includes('Deleter');
});

const fetchData = () => {
  usersStore.fetchUsers({ include_deleted: includeDeleted.value });
};

onMounted(fetchData);

const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return usersStore.users;
  }
  return usersStore.users.filter(user => 
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const getNestedValue = (item, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], item);
}

const openCreateModal = () => {
  isEditing.value = false;
  selectedUser.value = { email: '', password: '', role_id: null, is_active: true };
  isModalOpen.value = true;
};

const openEditModal = (user) => {
  isEditing.value = true;
  selectedUser.value = { ...user };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedUser.value = null;
};

const handleSave = async (userData) => {
  if (isEditing.value) {
    await usersStore.updateUser(userData.id, userData);
  } else {
    await usersStore.createUser(userData);
  }
  closeModal();
  fetchData();
};

const confirmDelete = (user, type) => {
  const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
  if (window.confirm(`Are you sure you want to ${action} ${user.email}?`)) {
    const deleteAction = type === 'soft' ? usersStore.softDeleteUser : usersStore.hardDeleteUser;
    deleteAction(user.id).then(fetchData);
  }
};

const restoreUser = (userId) => {
  if (window.confirm('Are you sure you want to restore this user?')) {
    usersStore.restoreUser(userId).then(fetchData);
  }
};
</script>
