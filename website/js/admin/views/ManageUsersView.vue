<!--
 * FILENAME: website/js/admin/views/ManageUsersView.vue
 * DESCRIPTION: View component for the 'Manage Users' page, now with interactive modals.
 *
 * This component now includes modals for adding and editing users. It manages the
 * state for which modal is open and which user is being edited. It uses the new
 * Modal and UserForm components to provide a seamless admin experience.
 *
 * UPDATED: Connected the form submission and delete buttons to the Pinia store actions.
-->
<template>
  <AdminLayout>
    <div class="bg-white p-8 rounded-lg shadow-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Manage Users</h1>
        <button @click="openAddUserModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add User
        </button>
      </div>

      <!-- Loading and Error States -->
      <div v-if="userStore.isLoading" class="text-center py-10">Loading users...</div>
      <div v-else-if="userStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        {{ userStore.error }}
      </div>

      <!-- Data Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full bg-white">
          <thead class="bg-gray-800 text-white">
            <tr>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">ID</th>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Email</th>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Name</th>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Role</th>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Verified</th>
              <th class="text-left py-3 px-4 uppercase font-semibold text-sm">Actions</th>
            </tr>
          </thead>
          <tbody class="text-gray-700">
            <tr v-for="user in userStore.users" :key="user.id" class="border-b border-gray-200 hover:bg-gray-100">
              <td class="py-3 px-4">{{ user.id }}</td>
              <td class="py-3 px-4">{{ user.email }}</td>
              <td class="py-3 px-4">{{ user.first_name }} {{ user.last_name }}</td>
              <td class="py-3 px-4"><span class="bg-blue-200 text-blue-800 py-1 px-3 rounded-full text-xs">{{ user.role }}</span></td>
              <td class="py-3 px-4"><span :class="user.is_verified ? 'text-green-500' : 'text-red-500'">{{ user.is_verified ? 'Yes' : 'No' }}</span></td>
              <td class="py-3 px-4">
                <button @click="openEditUserModal(user)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                <button @click="handleDeleteUser(user)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Edit/Add Modal -->
    <Modal :show="isModalOpen" @close="closeModal">
      <template #header>
        <h2 class="text-2xl font-bold">{{ modalMode === 'add' ? 'Add New User' : 'Edit User' }}</h2>
      </template>
      <template #body>
        <UserForm 
          :initial-data="currentUser" 
          @submit="handleFormSubmit"
          @cancel="closeModal"
        />
      </template>
      <template #footer>
        <!-- Footer is handled inside UserForm -->
        <div></div>
      </template>
    </Modal>

  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminUserStore } from '../../stores/adminUsers';
import AdminLayout from '../components/AdminLayout.vue';
import Modal from '../components/Modal.vue';
import UserForm from '../components/UserForm.vue';

const userStore = useAdminUserStore();

const isModalOpen = ref(false);
const modalMode = ref('add'); // 'add' or 'edit'
const currentUser = ref({});

onMounted(() => {
  userStore.fetchUsers();
});

const openAddUserModal = () => {
  modalMode.value = 'add';
  currentUser.value = { email: '', first_name: '', last_name: '', role: 'user', is_verified: false };
  isModalOpen.value = true;
};

const openEditUserModal = (user) => {
  modalMode.value = 'edit';
  // Create a deep copy to prevent reactive changes to the table while editing
  currentUser.value = JSON.parse(JSON.stringify(user));
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  currentUser.value = {};
};

const handleFormSubmit = async (userData) => {
  let success = false;
  if (modalMode.value === 'add') {
    success = await userStore.createUser(userData); 
  } else {
    success = await userStore.updateUser(userData.id, userData);
  }
  
  if (success) {
    closeModal();
  }
};

const handleDeleteUser = async (user) => {
  if (confirm(`Are you sure you want to delete user ${user.email}? This cannot be undone.`)) {
    await userStore.deleteUser(user.id);
  }
};
</script>
