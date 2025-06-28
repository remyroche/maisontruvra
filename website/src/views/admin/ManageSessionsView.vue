<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Sessions</h1>
    <div v-if="systemStore.error" class="text-red-500">{{ systemStore.error }}</div>
    <div>
      <table class="min-w-full bg-white">
        <thead>
          <tr>
            <th class="py-2">User ID</th>
            <th class="py-2">IP Address</th>
            <th class="py-2">Last Seen</th>
            <th class="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in systemStore.sessions" :key="session.id">
            <td class="border px-4 py-2">{{ session.user_id }}</td>
            <td class="border px-4 py-2">{{ session.ip_address }}</td>
            <td class="border px-4 py-2">{{ new Date(session.last_seen).toLocaleString() }}</td>
            <td class="border px-4 py-2">
              <button @click="terminateSession(session.id)" class="bg-red-500 text-white px-4 py-2 rounded">Terminate</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminSystemStore } from '@/js/stores/adminSystem';

const systemStore = useAdminSystemStore();

onMounted(() => {
  systemStore.fetchSessions();
});

const terminateSession = (sessionId) => {
    systemStore.terminateSession(sessionId);
};
</script>
