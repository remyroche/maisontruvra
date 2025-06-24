<template>
  <section aria-labelledby="summary-heading" class="rounded-lg bg-gray-50 px-4 py-6 sm:p-6 lg:col-span-5 lg:mt-0 lg:p-8">
    <h2 id="summary-heading" class="text-lg font-medium text-gray-900">Résumé de la commande</h2>

    <dl class="mt-6 space-y-4">
      <div class="flex items-center justify-between">
        <dt class="text-sm text-gray-600">Sous-total</dt>
        <dd class="text-sm font-medium text-gray-900">{{ cartStore.subtotal }} €</dd>
      </div>
      <div class="flex items-center justify-between border-t border-gray-200 pt-4">
        <dt class="flex items-center text-sm text-gray-600">
          <span>Frais de port</span>
        </dt>
        <dd class="text-sm font-medium text-gray-900">{{ shippingCost.toFixed(2) }} €</dd>
      </div>
      <div class="flex items-center justify-between border-t border-gray-200 pt-4">
        <dt class="text-base font-medium text-gray-900">Total</dt>
        <dd class="text-base font-medium text-gray-900">{{ totalWithShipping.toFixed(2) }} €</dd>
      </div>
    </dl>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useCartStore } from '../../js/stores/cart';
import { useCheckoutStore } from '../../js/stores/checkout';

const cartStore = useCartStore();
const checkoutStore = useCheckoutStore();

/**
 * Computes the shipping cost based on the selected delivery method.
 * @returns {number} The shipping cost as a number.
 */
const shippingCost = computed(() => {
    if (checkoutStore.deliveryMethod && typeof checkoutStore.deliveryMethod.price === 'number') {
        return checkoutStore.deliveryMethod.price;
    }
    return 0.00;
});

/**
 * Computes the final total by adding the cart subtotal and the shipping cost.
 * This is now fully reactive to changes in the selected delivery method.
 * @returns {number} The final total price.
 */
const totalWithShipping = computed(() => {
    const subtotal = parseFloat(cartStore.subtotal);
    return subtotal + shippingCost.value;
});

</script>
