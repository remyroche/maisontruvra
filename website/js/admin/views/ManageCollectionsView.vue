<!--
 * FILENAME: website/js/admin/views/ManageCollectionsView.vue
 * DESCRIPTION: View for managing product collections, now fully implemented.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-800">Manage Collections</h1>
        <button @click="openAddModal" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
          + Add Collection
        </button>
      </header>

      <div v-if="collectionStore.isLoading && !collectionStore.collections.length" class="text-center py-10">Loading collections...</div>
      <div v-else-if="collectionStore.error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
        {{ collectionStore.error }}
      </div>
      
      <BaseDataTable v-else :columns="columns" :data="collectionStore.collections">
        <template #cell(is_active)="{ value }">
             <span :class="value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                   class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ value ? 'Active' : 'Inactive' }}
             </span>
        </template>
        <template #cell(actions)="{ item }">
             <button @click="openEditModal(item)" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-2 rounded text-xs mr-2">Edit</button>
             <button @click="handleDelete(item)" class="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded text-xs">Delete</button>
        </template>
      </BaseDataTable>
    </div>

    <!-- Add/Edit Modal -->
    <Modal :show="isModalOpen" @close="closeModal">
      <template #header>
        <h2 class="text-2xl font-bold">{{ isEditing ? 'Edit Collection' : 'Add New Collection' }}</h2>
      </template>
      <template #body>
        <CollectionForm :initial-data="currentItem" @submit="handleSubmit" @cancel="closeModal" />
      </template>
      <template #footer><div></div></template>
    </Modal>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminCollectionStore } from '../../stores/adminCollections';
import { useAdminNotificationStore } from '../../stores/adminNotifications';

import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import Modal from '../components/Modal.vue';
import CollectionForm from '../components/CollectionForm.vue';

const collectionStore = useAdminCollectionStore();
const notificationStore = useAdminNotificationStore();

const isModalOpen = ref(false);
const currentItem = ref({});
const isEditing = computed(() => !!currentItem.value.id);

const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'description', label: 'Description' },
    { key: 'is_active', label: 'Status' },
    { key: 'actions', label: 'Actions', cellClass: 'text-right' },
];

onMounted(() => {
  collectionStore.fetchCollections();
});

const openAddModal = () => {
  currentItem.value = { name: '', description: '', is_active: true };
  isModalOpen.value = true;
};

const openEditModal = (item) => {
  currentItem.value = JSON.parse(JSON.stringify(item));
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const handleSubmit = async (data) => {
  const success = isEditing.value
    ? await collectionStore.updateCollection(data.id, data)
    : await collectionStore.createCollection(data);
  
  if (success) {
    closeModal();
    notificationStore.addNotification({
        type: 'success',
        title: `Collection ${isEditing.value ? 'Updated' : 'Created'}`,
    });
  } else {
     notificationStore.addNotification({ type: 'error', title: 'Save Failed', message: collectionStore.error });
  }
};

const handleDelete = async (item) => {
  if (confirm(`Are you sure you want to delete collection "${item.name}"?`)) {
    const success = await collectionStore.deleteCollection(item.id);
    if(success) {
        notificationStore.addNotification({ type: 'success', title: 'Collection Deleted' });
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Delete Failed', message: collectionStore.error });
    }
  }
};
</script>
