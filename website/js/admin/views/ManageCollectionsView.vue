<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Product Collections</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="md:col-span-2">
         <BaseDataTable :headers="headers" :items="collectionsStore.collections">
             <template #item-actions="{ item }">
                 <button @click="openModal(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
                 <button @click="deleteCollection(item.id)" class="text-red-600 hover:text-red-900">Delete</button>
             </template>
        </BaseDataTable>
      </div>
      <div>
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit Collection' : 'New Collection' }}</h2>
        <div class="bg-white p-4 rounded shadow">
          <CollectionForm :collection="selectedCollection" @save="saveCollection" :key="formKey" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminCollectionsStore } from '@/js/stores/adminCollections';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import CollectionForm from '@/js/admin/components/CollectionForm.vue';

const collectionsStore = useAdminCollectionsStore();
const isEditing = ref(false);
const selectedCollection = ref({ name: '', description: '' });
const formKey = ref(0);

const headers = [
    { text: 'Name', value: 'name' },
    { text: 'Description', value: 'description' },
    { text: 'Actions', value: 'actions' },
];

onMounted(() => collectionsStore.fetchCollections());

const openModal = (collection) => {
    isEditing.value = true;
    selectedCollection.value = { ...collection };
    formKey.value++;
};

const saveCollection = async (data) => {
    if(isEditing.value) {
        await collectionsStore.updateCollection(selectedCollection.value.id, data);
    } else {
        await collectionsStore.createCollection(data);
    }
    isEditing.value = false;
    selectedCollection.value = { name: '', description: '' };
    formKey.value++;
};

const deleteCollection = (id) => {
    if(confirm('Are you sure? This will not delete the products within it.')) {
        collectionsStore.deleteCollection(id);
    }
};
</script>
