<!--
 * FILENAME: website/js/admin/views/AuditLogView.vue
 * DESCRIPTION: View for displaying the admin audit log.
-->
<template>
    <AdminLayout>
        <div class="space-y-6">
             <header>
                <h1 class="text-3xl font-bold text-gray-800">Audit Log</h1>
                <p class="text-gray-500 mt-1">A log of all administrative actions performed.</p>
            </header>

            <div v-if="logStore.isLoading" class="text-center py-10">Loading logs...</div>
            <div v-else-if="logStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ logStore.error }}</div>

            <BaseDataTable v-else :columns="columns" :data="logStore.logs">
                 <template #cell(timestamp)="{ value }">
                    {{ new Date(value).toLocaleString() }}
                </template>
            </BaseDataTable>
        </div>
    </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminAuditLogStore } from '../../stores/adminAuditLog';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const logStore = useAdminAuditLogStore();

const columns = [
    { key: 'timestamp', label: 'Date' },
    { key: 'admin_email', label: 'Admin' },
    { key: 'action', label: 'Action' },
    { key: 'details', label: 'Details' },
];

onMounted(() => { logStore.fetchLogs(); });
</script>
