<!--
 * FILENAME: website/js/admin/views/ManageB2BView.vue
 * DESCRIPTION: View for managing B2B account applications.
-->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <header>
                <h1 class="text-3xl font-bold text-gray-800">Manage B2B Accounts</h1>
            </header>

            <div v-if="b2bStore.isLoading" class="text-center py-10">Loading accounts...</div>
            <div v-else-if="b2bStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ b2bStore.error }}</div>

            <BaseDataTable v-else :columns="columns" :data="b2bStore.accounts">
                <template #cell(status)="{ value }">
                    <span :class="statusClass(value)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                        {{ value }}
                    </span>
                </template>
                <template #cell(actions)="{ item }">
                    <div v-if="item.status === 'Pending'">
                        <button @click="handleStatusUpdate(item.id, true)" class="bg-green-500 text-white font-bold py-1 px-2 rounded text-xs mr-2">Approve</button>
                        <button @click="handleStatusUpdate(item.id, false)" class="bg-red-500 text-white font-bold py-1 px-2 rounded text-xs">Reject</button>
                    </div>
                </template>
            </BaseDataTable>
        </div>
    </AdminLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAdminB2BStore } from '../../stores/adminB2B';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const b2bStore = useAdminB2BStore();
const notificationStore = useAdminNotificationStore();

const columns = [
    { key: 'id', label: 'ID' },
    { key: 'company_name', label: 'Company Name' },
    { key: 'contact_name', label: 'Contact Name' },
    { key: 'contact_email', label: 'Contact Email' },
    { key: 'status', label: 'Status' },
    { key: 'actions', label: 'Actions', cellClass: 'text-right' }
];

onMounted(() => { b2bStore.fetchAccounts(); });

const handleStatusUpdate = async (id, is_approved) => {
    const action = is_approved ? 'approve' : 'reject';
    if (confirm(`Are you sure you want to ${action} this account?`)) {
        const success = await b2bStore.updateAccountStatus(id, is_approved);
        if (success) {
            notificationStore.addNotification({ type: 'success', title: 'Account Status Updated' });
        } else {
            notificationStore.addNotification({ type: 'error', title: 'Update Failed', message: b2bStore.error });
        }
    }
};

const statusClass = (status) => {
    const classes = {
        'Approved': 'bg-green-100 text-green-800',
        'Pending': 'bg-yellow-100 text-yellow-800',
        'Rejected': 'bg-red-100 text-red-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
}
</script>
