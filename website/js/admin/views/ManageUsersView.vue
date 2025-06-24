<!--
 * FILENAME: website/js/admin/views/ManageUsersView.vue
 * DESCRIPTION: View component for 'Manage Users', updated to use BaseDataTable.
 * UPDATED: Replaced the hardcoded table with the new reusable BaseDataTable component.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-800">Manage Users</h1>
        <button @click="openAddUserModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add User
        </button>
      </header>

      <div v-if="userStore.isLoading && !userStore.users.length" class="text-center py-10">Loading users...</div>
      <div v-else-if="userStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
        {{ userStore.error }}
      </div>
      
      <BaseDataTable v-else :columns="userColumns" :data="userStore.users">
        <!-- Custom cell rendering for 'role' -->
        <template #cell(role)="{ value }">
            <span class="bg-blue-200 text-blue-800 py-1 px-3 rounded-full text-xs font-medium">{{ value }}</span>
        </template>
        <!-- Custom cell rendering for 'is_verified' -->
        <template #cell(is_verified)="{ value }">
             <span :class="value ? 'text-green-600' : 'text-red-600'" class="font-bold">
                  {{ value ? 'Yes' : 'No' }}
             </span>
        </template>
        <!-- Custom cell rendering for 'actions' -->
        <template #cell(actions)="{ item }">
             <button @click="openEditUserModal(item)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
             <button @click="handleDeleteUser(item)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
        </template>
      </BaseDataTable>
    </div>

    <!-- User Edit/Add Modal (no changes) -->
    <Modal :show="isModalOpen" @close="closeModal">
      <template #header><h2 class="text-2xl font-bold">{{ modalMode === 'add' ? 'Add New User' : 'Edit User' }}</h2></template>
      <template #body><UserForm :initial-data="currentUser" @submit="handleFormSubmit" @cancel="closeModal"/></template>
      <template #footer><div></div></template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminUserStore } from '../../stores/adminUsers';
import { useAdminNotificationStore } from '../../stores/adminNotifications';

import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import Modal from '../components/Modal.vue';
import UserForm from '../components/UserForm.vue';

const userStore = useAdminUserStore();
const notificationStore = useAdminNotificationStore();

const isModalOpen = ref(false);
const modalMode = ref('add');
const currentUser = ref({});

const userColumns = [
    { key: 'id', label: 'ID' },
    { key: 'email', label: 'Email' },
    { key: 'first_name', label: 'First Name' },
    { key: 'role', label: 'Role' },
    { key: 'is_verified', label: 'Verified'},
    { key: 'actions', label: 'Actions', cellClass: 'text-right' },
];

onMounted(() => { userStore.fetchUsers(); });

const openAddUserModal = () => { /* ... no changes ... */ };
const openEditUserModal = (user) => { /* ... no changes ... */ };
const closeModal = () => { /* ... no changes ... */ };

const handleFormSubmit = async (userData) => {
  const isEdit = !!userData.id;
  const success = isEdit
    ? await userStore.updateUser(userData.id, userData)
    : await userStore.createUser(userData);
  
  if (success) {
    closeModal();
    notificationStore.addNotification({
        type: 'success',
        title: `User ${isEdit ? 'Updated' : 'Created'}`,
        message: `User ${userData.email} has been saved successfully.`,
    });
  } else {
     notificationStore.addNotification({
        type: 'error',
        title: 'Save Failed',
        message: userStore.error,
    });
  }
};

const handleDeleteUser = async (user) => {
  if (confirm(`Are you sure you want to delete user ${user.email}?`)) {
    const success = await userStore.deleteUser(user.id);
    if(success) {
        notificationStore.addNotification({ type: 'success', title: 'User Deleted', message: `User ${user.email} has been removed.`});
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Delete Failed', message: userStore.error });
    }
  }
};
</script>
