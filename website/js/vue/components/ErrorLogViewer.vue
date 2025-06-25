<!-- File 3: website/js/vue/components/ErrorLogViewer.vue -->
<!-- This Vue component fetches and displays the logs on the admin dashboard. -->

<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Dernières Erreurs (Fichier Log)</h3>
    <div v-if="loading" class="text-center text-gray-500">
      Chargement des logs...
    </div>
    <div v-else-if="error" class="text-center text-red-500 p-4 bg-red-50 rounded-lg">
      <p class="font-bold">Erreur de chargement</p>
      <p>{{ error }}</p>
    </div>
    <div v-else-if="logs.length === 0" class="text-center text-green-600 p-4 bg-green-50 rounded-lg">
      <p>✅ Aucune erreur critique trouvée dans les journaux récents.</p>
    </div>
    <div v-else class="overflow-x-auto">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-3 text-left font-semibold text-gray-600">Timestamp</th>
            <th class="p-3 text-left font-semibold text-gray-600">Niveau</th>
            <th class="p-3 text-left font-semibold text-gray-600">Message</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="(log, index) in logs" :key="index" class="hover:bg-gray-50">
            <td class="p-3 whitespace-nowrap text-gray-500 font-mono text-xs">{{ log.timestamp }}</td>
            <td class="p-3 whitespace-nowrap">
              <span class="font-bold rounded-full px-2 py-1 text-xs" :class="levelColor(log.level)">
                {{ log.level }}
              </span>
            </td>
            <td class="p-3 text-gray-800 break-words">
              <code class="text-xs">{{ log.message }}</code>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { apiClient } from '@/js/api-client.js'; // Adjust path if necessary

const loading = ref(true);
const error = ref(null);
const logs = ref([]);

const fetchErrorLogs = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/admin/monitoring/latest-errors?limit=20');
    logs.value = response.data;
  } catch (err) {
    error.value = "Impossible de récupérer les journaux d'erreurs depuis le backend.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const levelColor = (level) => {
  switch (level) {
    case 'CRITICAL':
      return 'bg-red-200 text-red-900';
    case 'ERROR':
      return 'bg-red-100 text-red-800';
    case 'WARNING':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

onMounted(fetchErrorLogs);
</script>

<style scoped>
/* Add any specific styles if needed */
</style>