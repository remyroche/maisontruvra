<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-serif text-brand-dark-brown mb-6">Request a Quote</h1>
    <p class="mb-6 text-gray-600">
      Use this form to request a quote for bulk orders of our standard products or for special sourcing of custom items not in our catalog.
    </p>
    <QuoteForm @submit-quote="handleQuoteRequest" />
  </div>
</template>

<script setup>
import QuoteForm from '@/components/pro/QuoteForm.vue';
import { useB2BStore } from '@/stores/b2b';
import { useRouter } from 'vue-router';

const b2bStore = useB2BStore();
const router = useRouter();

const handleQuoteRequest = async (quoteData) => {
  try {
    await b2bStore.submitQuoteRequest(quoteData);
    // Redirect to a confirmation page or the B2B dashboard
    router.push({ name: 'B2BDashboard' }); 
    // Show success notification
  } catch (error) {
    console.error("Failed to submit quote request:", error);
    // Show error notification
  }
};
</script>
