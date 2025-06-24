<!--
 * FILENAME: website/js/admin/views/ManageLoyaltyView.vue
 * DESCRIPTION: View for managing customer loyalty tiers.
-->
<template>
    <AdminLayout>
        <div class="space-y-6">
            <header class="flex justify-between items-center">
                <h1 class="text-3xl font-bold text-gray-800">Manage Loyalty Tiers</h1>
                <button @click="openAddModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
                    + Add Tier
                </button>
            </header>

            <div v-if="loyaltyStore.isLoading" class="text-center py-10">Loading tiers...</div>
            <div v-else-if="loyaltyStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ loyaltyStore.error }}</div>
            
            <BaseDataTable v-else :columns="columns" :data="loyaltyStore.tiers">
                 <template #cell(min_spend)="{ value }">€{{ value.toFixed(2) }}</template>
                 <template #cell(multiplier)="{ value }">{{ value }}x</template>
                 <template #cell(actions)="{ item }">
                    <button @click="openEditModal(item)" class="bg-yellow-500 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
                    <button @click="handleDelete(item)" class="bg-red-500 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
                </template>
            </BaseDataTable>
        </div>

        <Modal :show="isModalOpen" @close="closeModal">
            <template #header><h2 class="text-2xl font-bold">{{ isEditing ? 'Edit Tier' : 'Add New Tier' }}</h2></template>
            <template #body><LoyaltyTierForm :initial-data="currentItem" @submit="handleSubmit" @cancel="closeModal" /></template>
            <template #footer><div></div></template>
        </Modal>
    </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminLoyaltyStore } from '../../stores/adminLoyalty';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import Modal from '../components/Modal.vue';
import LoyaltyTierForm from '../components/LoyaltyTierForm.vue';

const loyaltyStore = useAdminLoyaltyStore();
const notificationStore = useAdminNotificationStore();

const isModalOpen = ref(false);
const currentItem = ref({});
const isEditing = computed(() => !!currentItem.value.id);

const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Tier Name' },
    { key: 'min_spend', label: 'Min Spend' },
    { key: 'multiplier', label: 'Point Multiplier' },
    { key: 'actions', label: 'Actions', cellClass: 'text-right' }
];

onMounted(() => { loyaltyStore.fetchTiers(); });

const openAddModal = () => {
    currentItem.value = { name: '', min_spend: 0, multiplier: 1.0 };
    isModalOpen.value = true;
};
const openEditModal = (item) => {
    currentItem.value = JSON.parse(JSON.stringify(item));
    isModalOpen.value = true;
};
const closeModal = () => { isModalOpen.value = false; };

const handleSubmit = async (data) => {
    const success = isEditing.value ? await loyaltyStore.updateTier(data.id, data) : await loyaltyStore.createTier(data);
    if(success) {
        closeModal();
        notificationStore.addNotification({ type: 'success', title: `Tier ${isEditing.value ? 'Updated' : 'Created'}`});
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Save Failed', message: loyaltyStore.error });
    }
};

const handleDelete = async (item) => {
    if (confirm(`Are you sure you want to delete tier "${item.name}"?`)) {
        const success = await loyaltyStore.deleteTier(item.id);
        if (success) {
            notificationStore.addNotification({ type: 'success', title: 'Tier Deleted' });
        } else {
            notificationStore.addNotification({ type: 'error', title: 'Delete Failed', message: loyaltyStore.error });
        }
    }
};
</script>
