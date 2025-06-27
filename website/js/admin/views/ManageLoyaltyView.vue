<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">Manage Loyalty & Referral Program</h1>

    <!-- Tabs for navigation -->
    <div class="mb-6 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button @click="activeTab = 'loyalty'" :class="[activeTab === 'loyalty' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
          Loyalty Tiers
        </button>
        <button @click="activeTab = 'referral'" :class="[activeTab === 'referral' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
          Referral Rewards
        </button>
      </nav>
    </div>

    <!-- Loyalty Tiers Management -->
    <div v-if="activeTab === 'loyalty'">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-4">Existing Loyalty Tiers</h2>
           <BaseDataTable :items="loyaltyStore.tiers" :columns="loyaltyTierColumns">
             <template #actions="{ item }">
               <button @click="openEditForm(item, 'loyalty')" class="text-indigo-600 hover:text-indigo-900 mr-4 font-medium">Edit</button>
               <button @click="confirmDelete(item.id, 'loyalty')" class="text-red-600 hover:text-red-900 font-medium">Delete</button>
             </template>
           </BaseDataTable>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
           <h2 class="text-xl font-semibold mb-4">{{ isEditingLoyaltyTier ? 'Edit Tier' : 'Add New Tier' }}</h2>
          <LoyaltyTierForm :tier="selectedLoyaltyTier" @save="saveLoyaltyTier" :key="loyaltyFormKey" />
        </div>
      </div>
    </div>

    <!-- Referral Rewards Management -->
    <div v-if="activeTab === 'referral'">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-4">Existing Referral Reward Tiers</h2>
            <BaseDataTable :items="loyaltyStore.referralTiers" :columns="referralTierColumns">
                <template #actions="{ item }">
                    <button @click="openEditForm(item, 'referral')" class="text-indigo-600 hover:text-indigo-900 mr-4 font-medium">Edit</button>
                    <button @click="confirmDelete(item.id, 'referral')" class="text-red-600 hover:text-red-900 font-medium">Delete</button>
                </template>
            </BaseDataTable>
          </div>
          <div class="bg-white p-6 rounded-lg shadow">
            <h2 class="text-xl font-semibold mb-4">{{ isEditingReferralTier ? 'Edit Referral Reward' : 'Add New Referral Reward' }}</h2>
            <!-- Assume ReferralRewardForm exists or will be created -->
            <!-- <ReferralRewardForm :tier="selectedReferralTier" @save="saveReferralTier" :key="referralFormKey" /> -->
             <p class="text-gray-500">Referral reward form will be here.</p>
          </div>
      </div>
    </div>
    
    <ConfirmDialog ref="confirmDialog" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAdminLoyaltyStore } from '../../stores/adminLoyalty';
import BaseDataTable from '../components/ui/BaseDataTable.vue';
import LoyaltyTierForm from '../components/LoyaltyTierForm.vue';
// import ReferralRewardForm from '../components/ReferralRewardForm.vue'; // To be created
import ConfirmDialog from '../components/ConfirmDialog.vue';
import { useNotificationStore } from '../../stores/notification';

const loyaltyStore = useAdminLoyaltyStore();
const notificationStore = useNotificationStore();

// State for active tab
const activeTab = ref('loyalty');

// State for Loyalty Tiers
const isEditingLoyaltyTier = ref(false);
const selectedLoyaltyTier = ref({ name: '', min_spend: 0, points_per_euro: 1.0, benefits: '' });
const loyaltyFormKey = ref(0);
const confirmDialog = ref(null);


// State for Referral Tiers
const isEditingReferralTier = ref(false);
const selectedReferralTier = ref({ referral_count: 0, reward_description: '' });
const referralFormKey = ref(0);

const loyaltyTierColumns = [
    { key: 'name', label: 'Tier Name' },
    { key: 'min_spend', label: 'Min Spend (€)' },
    { key: 'points_per_euro', label: 'Points / €' },
    { key: 'benefits', label: 'Benefits' },
    { key: 'actions', label: 'Actions' },
];

const referralTierColumns = [
    { key: 'referral_count', label: 'Referral Count' },
    { key: 'reward_description', label: 'Reward Description' },
    { key: 'actions', label: 'Actions' },
];

onMounted(() => {
    loyaltyStore.fetchLoyaltyTiers();
    loyaltyStore.fetchReferralTiers();
});

const openEditForm = (item, type) => {
    if (type === 'loyalty') {
        isEditingLoyaltyTier.value = true;
        selectedLoyaltyTier.value = { ...item };
        loyaltyFormKey.value++;
    } else if (type === 'referral') {
        isEditingReferralTier.value = true;
        selectedReferralTier.value = { ...item };
        referralFormKey.value++;
    }
};

const resetLoyaltyForm = () => {
    isEditingLoyaltyTier.value = false;
    selectedLoyaltyTier.value = { name: '', min_spend: 0, points_per_euro: 1.0, benefits: '' };
    loyaltyFormKey.value++;
}

const saveLoyaltyTier = async (data) => {
    try {
        if (isEditingLoyaltyTier.value) {
            await loyaltyStore.updateTier(selectedLoyaltyTier.value.id, data);
            notificationStore.showNotification({ message: 'Loyalty tier updated!', type: 'success' });
        } else {
            await loyaltyStore.createTier(data);
            notificationStore.showNotification({ message: 'Loyalty tier created!', type: 'success' });
        }
        resetLoyaltyForm();
    } catch (error) {
        notificationStore.showNotification({ message: 'An error occurred.', type: 'error' });
    }
};

const confirmDelete = async (id, type) => {
    const isConfirmed = await confirmDialog.value.show({
        title: 'Confirm Deletion',
        message: `Are you sure you want to delete this ${type === 'loyalty' ? 'loyalty tier' : 'referral reward'}? This action cannot be undone.`,
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel'
    });

    if (isConfirmed) {
        if (type === 'loyalty') {
            await loyaltyStore.deleteTier(id);
            notificationStore.showNotification({ message: 'Loyalty tier deleted.', type: 'success' });
        } else if (type === 'referral') {
            await loyaltyStore.deleteReferralTier(id);
             notificationStore.showNotification({ message: 'Referral reward deleted.', type: 'success' });
        }
    }
};
</script>
