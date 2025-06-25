<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Users</h1>
    
    <div class="mb-4 flex justify-between">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search users..." 
        class="border rounded p-2 w-1/3"
      >
      <button @click="openCreateModal" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
        Create User
      </button>
    </div>

    <div v-if="usersStore.isLoading" class="text-center">Loading...</div>
    <div v-if="usersStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ usersStore.error }}</div>

    <BaseDataTable
      v-if="!usersStore.isLoading && filteredUsers.length"
      :headers="headers"
      :items="filteredUsers"
    >
      <template #item-is_active="{ item }">
        <span :class="item.is_active ? 'text-green-500' : 'text-red-500'">
          {{ item.is_active ? 'Yes' : 'No' }}
        </span>
      </template>
      <template #item-is_frozen="{ item }">
        <span :class="item.is_frozen ? 'text-blue-500' : 'text-gray-500'">
          {{ item.is_frozen ? 'Yes' : 'No' }}
        </span>
      </template>
      <template #item-actions="{ item }">
        <button @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
        <button @click="toggleFreeze(item)" class="mr-4" :class="item.is_frozen ? 'text-green-600 hover:text-green-900' : 'text-blue-600 hover:text-blue-900'">
            {{ item.is_frozen ? 'Unfreeze' : 'Freeze' }}
        </button>
        <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900">Delete</button>
      </template>
    </BaseDataTable>
    <div v-if="!usersStore.isLoading && !filteredUsers.length" class="text-center text-gray-500 mt-4">
        No users found.
    </div>

    <!-- Modal for Create/Edit -->
    <Modal :is-open="isModalOpen" @close="closeModal">
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit User' : 'Create User' }}</h2>
        <UserForm 
            :user="selectedUser" 
            @save="handleSave"
            @cancel="closeModal"
        />
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminUsersStore } from '@/js/stores/adminUsers';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';
import UserForm from '@/js/admin/components/UserForm.vue';

const usersStore = useAdminUsersStore();

const searchQuery = ref('');
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

onMounted(() => {
  usersStore.fetchUsers();
});

const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return usersStore.users;
  }
  return usersStore.users.filter(user => 
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const openCreateModal = () => {
    isEditing.value = false;
    selectedUser.value = { email: '', password: '', role_id: null, is_active: true, is_frozen: false };
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
};

const toggleFreeze = (user) => {
    if (user.is_frozen) {
        usersStore.unfreezeUser(user.id);
    } else {
        usersStore.freezeUser(user.id);
    }
};

const confirmDelete = (user) => {
    if (window.confirm(`Are you sure you want to delete ${user.email}?`)) {
        usersStore.deleteUser(user.id);
    }
};

</script>
