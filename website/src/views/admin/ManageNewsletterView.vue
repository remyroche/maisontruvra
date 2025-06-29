<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Newsletter Management</h1>
    
    <div class="mb-4 flex justify-between items-center">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search subscribers..." 
        class="border rounded p-2 w-1/3"
      >
      <button @click="openCampaignModal" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Create Campaign
      </button>
    </div>

    <div v-if="isLoading" class="text-center p-4">Loading subscribers...</div>
    <div v-if="error" class="text-red-500 bg-red-100 p-4 rounded">{{ error }}</div>

    <BaseDataTable
      v-if="!isLoading && filteredSubscribers.length"
      :headers="headers"
      :items="filteredSubscribers"
    >
      <template #item-subscribed_at="{ item }">
        <span>{{ new Date(item.subscribed_at).toLocaleString() }}</span>
      </template>
      <template #item-actions="{ item }">
        <button @click="confirmDelete(item)" class="text-red-600 hover:text-red-900">Unsubscribe</button>
      </template>
    </BaseDataTable>
    <div v-if="!isLoading && !filteredSubscribers.length" class="text-center text-gray-500 mt-8">
        No subscribers found.
    </div>

    <!-- Modal for Create Campaign -->
    <Modal :is-open="isModalOpen" @close="closeCampaignModal">
        <h2 class="text-xl font-bold mb-4">Compose Newsletter</h2>
        <form @submit.prevent="handleSendCampaign" class="space-y-4">
            <div>
                <label for="subject" class="block text-sm font-medium">Subject</label>
                <input id="subject" v-model="campaign.subject" type="text" required class="mt-1 block w-full border p-2 rounded">
            </div>

            <!-- Targeting Options -->
            <div class="border-t pt-4">
                <h3 class="text-lg font-medium text-gray-800">Targeting</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    <div>
                        <label for="target-audience" class="block text-sm font-medium">Audience</label>
                        <select v-model="campaign.targetAudience" id="target-audience" class="mt-1 block w-full border p-2 rounded">
                            <option value="all">All Subscribers</option>
                            <option value="b2c">B2C Users Only</option>
                            <option value="b2b">B2B Users Only</option>
                        </select>
                    </div>
                    <div>
                        <label for="target-language" class="block text-sm font-medium">Language</label>
                        <select v-model="campaign.language" id="target-language" class="mt-1 block w-full border p-2 rounded">
                            <option value="all">All Languages</option>
                            <option value="en">English</option>
                            <option value="fr">Français</option>
                        </select>
                    </div>
                </div>
                <!-- B2B Loyalty Tiers filter -->
                <div v-if="campaign.targetAudience === 'b2b' && loyaltyTiers.length" class="mt-4">
                     <label class="block text-sm font-medium">B2B Loyalty Tiers (Optional)</label>
                     <p class="text-xs text-gray-500 mb-2">Select tiers to target. Leave all unchecked to target all B2B users.</p>
                     <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                        <div v-for="tier in loyaltyTiers" :key="tier.id" class="flex items-center">
                            <input 
                                :id="`tier-${tier.id}`" 
                                :value="tier.id"
                                v-model="campaign.targetTiers"
                                type="checkbox" 
                                class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                            >
                            <label :for="`tier-${tier.id}`" class="ml-2 block text-sm text-gray-900">{{ tier.name }}</label>
                        </div>
                     </div>
                </div>
            </div>

            <div>
                <label for="content" class="block text-sm font-medium">HTML Content</label>
                <textarea id="content" v-model="campaign.html_content" rows="12" required class="mt-1 block w-full border p-2 rounded font-mono"></textarea>
            </div>

            <div class="flex justify-end space-x-2">
                <button type="button" @click="closeCampaignModal" class="bg-gray-200 px-4 py-2 rounded">Cancel</button>
                <button type="submit" :disabled="isSending" class="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50">
                    <span v-if="!isSending">Send Campaign</span>
                    <span v-else>Sending...</span>
                </button>
            </div>
        </form>
    </Modal>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BaseDataTable from '@/components/ui/BaseDataTable.vue';
import Modal from '@/components/ui/Modal.vue';
import api from '@/services/api';

const notificationStore = useNotificationStore();

const subscribers = ref([]);
const loyaltyTiers = ref([]);
const isLoading = ref(true);
const isSending = ref(false);
const error = ref(null);

const searchQuery = ref('');
const isModalOpen = ref(false);

const campaign = reactive({
    subject: '',
    html_content: '',
    targetAudience: 'all',
    language: 'all',
    targetTiers: [],
});

const headers = [
  { text: 'Email', value: 'email' },
  { text: 'Subscription Date', value: 'subscribed_at' },
  { text: 'Actions', value: 'actions', sortable: false },
];

async function fetchSubscribers() {
    try {
        const response = await apiClient.get('/admin/newsletter/subscribers');
        subscribers.value = response.data;
    } catch (err) {
        error.value = 'Failed to load subscribers.';
        notificationStore.showNotification(error.value, 'error');
    }
}

async function fetchLoyaltyTiers() {
    try {
        const response = await apiClient.get('/admin/loyalty/tiers');
        loyaltyTiers.value = response.data;
    } catch (err) {
        // Non-critical, so we don't block the UI
        console.error('Failed to load loyalty tiers:', err);
    }
}

onMounted(async () => {
    isLoading.value = true;
    await Promise.all([
        fetchSubscribers(),
        fetchLoyaltyTiers()
    ]);
    isLoading.value = false;
});

const filteredSubscribers = computed(() => {
  if (!searchQuery.value) {
    return subscribers.value;
  }
  return subscribers.value.filter(sub => 
    sub.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const confirmDelete = async (subscriber) => {
    if (window.confirm(`Are you sure you want to unsubscribe ${subscriber.email}?`)) {
        try {
            await apiClient.delete(`/admin/newsletter/subscribers/${subscriber.id}`);
            notificationStore.showNotification('Subscriber removed.', 'success');
            await fetchSubscribers();
        } catch (err) {
            notificationStore.showNotification('Failed to remove subscriber.', 'error');
        }
    }
};

const openCampaignModal = () => {
    isModalOpen.value = true;
};
const closeCampaignModal = () => {
    isModalOpen.value = false;
    // Reset campaign object
    campaign.subject = '';
    campaign.html_content = '';
    campaign.targetAudience = 'all';
    campaign.language = 'all';
    campaign.targetTiers = [];
};

const handleSendCampaign = async () => {
    if (confirm(`This will send the newsletter to the specified audience. Are you sure?`)) {
        isSending.value = true;
        try {
            const response = await apiClient.post('/admin/newsletter/send', campaign);
            notificationStore.showNotification(response.data.message || 'Campaign sent successfully!', 'success');
            closeCampaignModal();
        } catch(err) {
            notificationStore.showNotification(err.response?.data?.error || 'An error occurred.', 'error');
        } finally {
            isSending.value = false;
        }
    }
};
</script>
