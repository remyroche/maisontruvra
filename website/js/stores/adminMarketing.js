import { defineStore } from 'pinia';
import apiClient from '@/js/common/adminApiClient';

export const useAdminMarketingStore = defineStore('adminMarketing', {
  state: () => ({
    subscribers: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchSubscribers() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/newsletter/subscribers');
        this.subscribers = response.data;
      } catch (e) {
        this.error = 'Failed to fetch subscribers.';
        console.error(this.error, e);
      } finally {
        this.isLoading = false;
      }
    },
    async deleteSubscriber(subscriberId) {
        try {
            await apiClient.delete(`/newsletter/subscribers/${subscriberId}`);
            await this.fetchSubscribers(); // Refresh the list
        } catch (e) {
            this.error = "Failed to delete subscriber.";
            console.error(this.error, e);
        }
    },
    async sendNewsletter(campaignData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.post('/newsletter/send', campaignData);
        return response.data; // Return success message
      } catch (e) {
        this.error = 'Failed to send newsletter.';
        console.error(this.error, e);
        throw e;
      } finally {
        this.isLoading = false;
      }
    },
  },
});

    return { subscribers, quotes, isLoading, error, fetchSubscribers, fetchQuotes };
});
