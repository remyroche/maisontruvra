<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Audit Log</h1>
     <BaseDataTable v-if="!logStore.isLoading" :headers="headers" :items="logStore.logs" />
     <div v-else>Loading logs...</div>
  </div>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminAuditLogStore } from '@/js/stores/adminAuditLog';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const logStore = useAdminAuditLogStore();
const headers = [
    { text: 'Timestamp', value: 'timestamp' },
    { text: 'Admin User', value: 'admin_user_email' },
    { text: 'Action', value: 'action' },
    { text: 'Details', value: 'details' },
];
onMounted(() => logStore.fetchLogs());
</script>

