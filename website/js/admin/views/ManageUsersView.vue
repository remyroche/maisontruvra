<!--
 * FILENAME: website/js/admin/views/ManageUsersView.vue
 * DESCRIPTION: View component for the 'Manage Users' page.
 *
 * This component is responsible for displaying the user data table
 * and handling user interactions like editing, deleting, or creating users.
 * It fetches data from the useAdminUserStore and manages loading/error states.
-->
<template>
  <AdminLayout>
    <div class="bg-white p-8 rounded-lg shadow-md">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Manage Users</h1>
        <button class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add User
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="userStore.isLoading" class="text-center py-10">
        <p class="text-gray-500">Loading users...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="userStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Error:</strong>
        <span class="block sm:inline">{{ userStore.error }}</span>
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
              <td class="py-3 px-4">
                <span class="bg-blue-200 text-blue-800 py-1 px-3 rounded-full text-xs">{{ user.role }}</span>
              </td>
              <td class="py-3 px-4">
                <span :class="user.is_verified ? 'text-green-500' : 'text-red-500'">
                  {{ user.is_verified ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="py-3 px-4">
                <button @click="editUser(user)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminUserStore } from '../../stores/adminUsers';
import AdminLayout from '../components/AdminLayout.vue';

const userStore = useAdminUserStore();

// Fetch users when the component is mounted
onMounted(() => {
  userStore.fetchUsers();
});

function editUser(user) {
  // Placeholder for edit functionality
  alert(`Editing user: ${user.email}`);
  // In a real implementation, this would open a modal or navigate to an edit page.
}
</script>
