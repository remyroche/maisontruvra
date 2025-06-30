<template>
  <div class="p-6 sm:p-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-bold text-gray-900">Session Management</h1>
        <p class="mt-2 text-sm text-gray-700">Monitor and manage all active user sessions on the platform.</p>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="systemStore.error" class="mt-4 rounded-md bg-red-50 p-4">
        <h3 class="text-sm font-medium text-red-800">Error Loading Sessions</h3>
        <p class="mt-2 text-sm text-red-700">{{ systemStore.error.message || 'An unknown error occurred.' }}</p>
    </div>

    <!-- Data Table -->
    <div class="mt-8 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <div class="relative">
            <!-- Loading Indicator -->
            <div v-if="systemStore.isLoading" class="absolute inset-0 z-10 flex items-center justify-center bg-white bg-opacity-75">
              <p>Loading sessions...</p> <!-- You can add a spinner component here -->
            </div>
            <table class="min-w-full table-fixed divide-y divide-gray-300">
              <thead>
                <tr>
                  <th scope="col" class="py-3.5 px-3 text-left text-sm font-semibold text-gray-900">User</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">IP Address</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Last Seen</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">User Agent</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-3">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="session in systemStore.sessions" :key="session.id">
                  <td class="whitespace-nowrap py-4 px-3 text-sm font-medium text-gray-900">{{ session.user.email }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ session.ip_address }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ formatDate(session.last_seen) }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 truncate" :title="session.user_agent">{{ session.user_agent.substring(0, 50) }}...</td>
                  <td class="whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-3">
                    <button @click="handleTerminateSession(session)" class="text-red-600 hover:text-red-900">
                      Terminate<span class="sr-only">, session for {{ session.user.email }}</span>
                    </button>
                  </td>
                </tr>
                 <tr v-if="!systemStore.isLoading && systemStore.sessions.length === 0">
                    <td colspan="5" class="text-center py-8 text-gray-500">No active sessions found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminSystemStore } from '@/stores/adminSystem'; // Using the specified store
import { useDateFormatter } from '@/composables/useDateFormatter';
import { useNotificationStore } from '@/stores/notification';

const systemStore = useAdminSystemStore();
const notificationStore = useNotificationStore();
const { formatDate } = useDateFormatter(); // For cleaner date display

onMounted(() => {
  // Fetch sessions using the store action
  systemStore.fetchSessions();
});

const handleTerminateSession = async (session) => {
  // Use a simple confirm dialog for security actions
  if (!confirm(`Are you sure you want to terminate the session for ${session.user.email}? This will force them to log out immediately.`)) {
    return;
  }
  
  try {
    // Call the store action to terminate the session
    await systemStore.terminateSession(session.id);
    notificationStore.addNotification('Session terminated successfully.', 'success');
  } catch (err) {
    // The store should handle its own errors, but we can catch and notify here too
    notificationStore.addNotification(err.message || 'Failed to terminate session.', 'error');
  }
};
</script>
