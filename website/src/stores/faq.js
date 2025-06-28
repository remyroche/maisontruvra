import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useFaqStore = defineStore('faq', () => {
  const faqs = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchFaqs() {
    if (faqs.value) return; // Don't re-fetch if already loaded

    isLoading.value = true;
    error.value = null;
    try {
      // Vite can directly import JSON files, which is very efficient.
      const faqData = await import('@/locales/faq.json');
      faqs.value = faqData.default; // The actual data is on the .default property
    } catch (e) {
      console.error('Failed to load FAQ data:', e);
      error.value = 'Could not load FAQ data. Please try again later.';
    } finally {
      isLoading.value = false;
    }
  }

  return { faqs, isLoading, error, fetchFaqs };
});