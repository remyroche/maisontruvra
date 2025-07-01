<template>
  <div class="p-6" v-if="quote">
    <h1 class="text-2xl font-semibold mb-2">Respond to Quote #{{ quote.id }}</h1>
    <p class="mb-4 text-gray-600">For: <strong>{{ quote.user.company_name }}</strong> ({{ quote.user.email }})</p>

    <div class="bg-white p-6 rounded-lg shadow-md">
      <form @submit.prevent="submitResponse">
        <div class="space-y-4">
          <h3 class="text-lg font-semibold border-b pb-2">Quoted Items</h3>
          
          <div v-for="item in form.items" :key="item.item_id" class="p-4 border rounded-md">
            <p class="font-semibold">{{ item.name }}</p>
            <p v-if="item.description" class="text-sm text-gray-500 mt-1">{{ item.description }}</p>
            <p class="text-sm mt-2">Requested Quantity: <strong>{{ item.quantity }}</strong></p>
            
            <div class="mt-2">
              <label :for="'price-' + item.item_id" class="block text-sm font-medium">Response Price (per item)</label>
              <div class="relative mt-1 rounded-md shadow-sm">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <span class="text-gray-500 sm:text-sm">€</span>
                </div>
                <input 
                  type="number" 
                  :id="'price-' + item.item_id" 
                  v-model.number="item.price" 
                  step="0.01" 
                  required 
                  class="block w-full rounded-md border-gray-300 pl-7 pr-12 focus:border-brand-burgundy focus:ring-brand-burgundy"
                  placeholder="0.00"
                >
              </div>
            </div>
          </div>
        </div>

        <div class="mt-8">
          <button type="submit" class="w-full bg-brand-burgundy text-white py-3 px-4 rounded-md hover:bg-opacity-90 transition-colors">
            Price Items & Add to User's Cart
          </button>
        </div>
      </form>
    </div>
  </div>
  <div v-else class="text-center py-16">
    <p>Loading quote details...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useB2BStore } from '@/stores/b2b';

const route = useRoute();
const router = useRouter();
const b2bStore = useB2BStore();

const quote = ref(null);
const form = reactive({ items: [] });

onMounted(async () => {
  const quoteId = route.params.id;
  await b2bStore.fetchQuoteDetails(quoteId);
  quote.value = b2bStore.currentQuote;

  if (quote.value) {
    form.items = quote.value.items.map(item => ({
      item_id: item.id,
      name: item.custom_item_name || item.product.name,
      description: item.custom_item_description || item.product.description,
      quantity: item.quantity,
      price: item.response_price || ''
    }));
  }
});

const submitResponse = async () => {
  try {
    const payload = { items: form.items.map(i => ({ item_id: i.item_id, price: i.price })) };
    await b2bStore.respondAndAddToCart(quote.value.id, payload);
    router.push({ name: 'AdminManageQuotes' });
    // Show success notification
  } catch (error) {
    console.error("Failed to respond to quote:", error);
    // Show error notification
  }
};
</script>
