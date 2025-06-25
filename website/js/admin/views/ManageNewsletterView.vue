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

    <div v-if="marketingStore.isLoading" class="text-center p-4">Loading...</div>
    <div v-if="marketingStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ marketingStore.error }}</div>

    <BaseDataTable
      v-if="!marketingStore.isLoading && filteredSubscribers.length"
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
    <div v-if="!marketingStore.isLoading && !filteredSubscribers.length" class="text-center text-gray-500 mt-8">
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
            <div>
                <label for="content" class="block text-sm font-medium">HTML Content</label>
                <textarea id="content" v-model="campaign.html_content" rows="12" required class="mt-1 block w-full border p-2 rounded font-mono"></textarea>
            </div>
             <div class="flex justify-end space-x-2">
                <button type="button" @click="closeCampaignModal" class="bg-gray-200 px-4 py-2 rounded">Cancel</button>
                <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded">Send to All Subscribers</button>
            </div>
        </form>
    </Modal>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useAdminMarketingStore } from '@/js/stores/adminMarketing';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';
import Modal from '@/js/admin/components/Modal.vue';

const marketingStore = useAdminMarketingStore();

const searchQuery = ref('');
const isModalOpen = ref(false);
const campaign = reactive({
    subject: '',
    html_content: '',
});

const headers = [
  { text: 'Email', value: 'email' },
  { text: 'Subscription Date', value: 'subscribed_at' },
  { text: 'Actions', value: 'actions', sortable: false },
];

onMounted(() => {
  marketingStore.fetchSubscribers();
});

const filteredSubscribers = computed(() => {
  if (!searchQuery.value) {
    return marketingStore.subscribers;
  }
  return marketingStore.subscribers.filter(sub => 
    sub.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const confirmDelete = (subscriber) => {
    if (window.confirm(`Are you sure you want to unsubscribe ${subscriber.email}?`)) {
        marketingStore.deleteSubscriber(subscriber.id);
    }
};

const openCampaignModal = () => {
    isModalOpen.value = true;
};
const closeCampaignModal = () => {
    isModalOpen.value = false;
    campaign.subject = '';
    campaign.html_content = '';
};

const handleSendCampaign = async () => {
    if (confirm(`This will send the newsletter to ${marketingStore.subscribers.length} subscribers. Are you sure?`)) {
        try {
            const response = await marketingStore.sendNewsletter(campaign);
            alert(response.message); // Show success message from backend
            closeCampaignModal();
        } catch(e) {
            // Error is handled in the store, but we can add UI feedback here if needed
            alert('An error occurred while sending the newsletter.');
        }
    }
};
</script>
