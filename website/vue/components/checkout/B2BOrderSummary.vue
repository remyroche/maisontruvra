<template>
  <section aria-labelledby="summary-heading" class="rounded-lg bg-gray-50 px-4 py-6 sm:p-6 lg:p-8">
    <h2 id="summary-heading" class="text-lg font-medium text-gray-900">Résumé de la Commande Professionnelle</h2>

    <dl class="mt-6 space-y-4">
      <div class="flex items-center justify-between">
        <dt class="text-sm text-gray-600">Sous-total HT</dt>
        <dd class="text-sm font-medium text-gray-900">{{ checkoutStore.subtotal.toFixed(2) }} €</dd>
      </div>

      <div class="flex items-center justify-between border-t border-gray-200 pt-4">
        <dt class="flex items-center text-sm text-gray-600">
          <span>Frais de port HT</span>
        </dt>
        <dd class="text-sm font-medium text-gray-900">{{ checkoutStore.shippingCost.toFixed(2) }} €</dd>
      </div>

      <div class="flex items-center justify-between">
        <dt class="text-sm text-gray-600">Total HT</dt>
        <dd class="text-sm font-medium text-gray-900">{{ checkoutStore.totalHT.toFixed(2) }} €</dd>
      </div>
      
      <div class="flex items-center justify-between border-t border-gray-200 pt-4">
        <dt class="flex items-center text-sm text-gray-600">
          <span>TVA ({{ (VAT_RATE * 100) }}%)</span>
        </dt>
        <dd class="text-sm font-medium text-gray-900">{{ vatAmount.toFixed(2) }} €</dd>
      </div>

      <div class="flex items-center justify-between text-lg font-medium text-gray-900 border-t border-gray-200 pt-4">
        <dt>Total TTC</dt>
        <dd>{{ totalTTC.toFixed(2) }} €</dd>
      </div>
    </dl>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useB2BCheckoutStore } from '../../js/stores/b2bCheckout';

const checkoutStore = useB2BCheckoutStore();
const VAT_RATE = 0.20; // Standard 20% VAT rate

/**
 * Calculates the VAT amount based on the total before tax.
 */
const vatAmount = computed(() => {
    return checkoutStore.totalHT * VAT_RATE;
});

/**
 * Calculates the final price including VAT. This value is reactive and
 * will automatically update whenever the delivery method changes.
 * This is the definitive price for payment and invoicing.
 */
const totalTTC = computed(() => {
    return checkoutStore.totalHT + vatAmount.value;
});
</script>
