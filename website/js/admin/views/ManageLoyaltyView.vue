<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Loyalty Program</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Tier List -->
      <div class="md:col-span-2">
        <h2 class="text-xl font-bold mb-4">Loyalty Tiers</h2>
         <BaseDataTable :headers="headers" :items="loyaltyStore.tiers">
             <template #item-actions="{ item }">
                 <button @click="openEditForm(item)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
                 <button @click="deleteTier(item.id)" class="text-red-600 hover:text-red-900">Delete</button>
             </template>
        </BaseDataTable>
      </div>

      <!-- Tier Form -->
      <div>
        <h2 class="text-xl font-bold mb-4">{{ isEditing ? 'Edit Tier' : 'New Tier' }}</h2>
        <div class="bg-white p-4 rounded shadow">
          <LoyaltyTierForm :tier="selectedTier" @save="saveTier" :key="formKey" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminLoyaltyStore } from '@/js/stores/adminLoyalty';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import LoyaltyTierForm from '@/js/admin/components/LoyaltyTierForm.vue';

const loyaltyStore = useAdminLoyaltyStore();
const isEditing = ref(false);
const selectedTier = ref({ name: '', min_points: 0, multiplier: 1.0 });
const formKey = ref(0); // To reset the form component

const headers = [
    { text: 'Tier Name', value: 'name' },
    { text: 'Minimum Points', value: 'min_points' },
    { text: 'Points Multiplier', value: 'multiplier' },
    { text: 'Actions', value: 'actions' },
];

onMounted(() => loyaltyStore.fetchTiers());

const openEditForm = (tier) => {
    isEditing.value = true;
    selectedTier.value = { ...tier };
    formKey.value++;
};

const saveTier = async (data) => {
    if(isEditing.value) {
        await loyaltyStore.updateTier(selectedTier.value.id, data);
    } else {
        await loyaltyStore.createTier(data);
    }
    // Reset form
    isEditing.value = false;
    selectedTier.value = { name: '', min_points: 0, multiplier: 1.0 };
    formKey.value++;
};

const deleteTier = (id) => {
    if(confirm('Are you sure you want to delete this tier?')) {
        loyaltyStore.deleteTier(id);
    }
};
</script>
