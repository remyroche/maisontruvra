<template>
  <section aria-labelledby="summary-heading" class="rounded-lg bg-white px-4 py-6 sm:p-6 lg:p-8 border border-gray-200 shadow-sm">
    <h2 id="summary-heading" class="text-lg font-medium text-gray-900">{{ $t('order_summary.title') }}</h2>

    <ul role="list" class="divide-y divide-gray-200 mt-6">
        <li v-for="item in cartStore.items" :key="item.id" class="flex py-6">
          <div class="flex-shrink-0">
            <img :src="item.product.image_url || '/static/assets/placeholder.png'" :alt="item.product.name" class="w-24 h-24 rounded-md object-center object-cover">
          </div>
          <div class="ml-4 flex-1 flex flex-col">
            <div>
              <div class="flex justify-between text-base font-medium text-gray-900">
                <h3>
                  <a :href="`/product/${item.product.id}`"> {{ item.product.name }} </a>
                </h3>
                <p v-if="!item.is_reward" class="ml-4">€{{ (item.product.price * item.quantity).toFixed(2) }}</p>
                <p v-else class="ml-4 text-primary font-bold">{{ $t('order_summary.free') }}</p>
              </div>
              <p v-if="item.is_reward" class="mt-1 text-sm text-primary font-semibold">{{ $t('order_summary.loyalty_reward') }}</p>
            </div>
            <div class="flex-1 flex items-end justify-between text-sm">
              <p class="text-gray-500">Qty {{ item.quantity }}</p>
            </div>
          </div>
        </li>
      </ul>

    <dl class="mt-6 space-y-4 border-t border-gray-200 pt-6">
      <div class="flex items-center justify-between">
        <dt class="text-sm text-gray-600">{{ $t('order_summary.subtotal') }}</dt>
        <dd class="text-sm font-medium text-gray-900">€{{ cartStore.subtotal.toFixed(2) }}</dd>
      </div>
      <div class="flex items-center justify-between">
        <dt class="text-sm text-gray-600">{{ $t('order_summary.shipping') }}</dt>
        <dd class="text-sm font-medium text-gray-900">€{{ shippingCost.toFixed(2) }}</dd>
      </div>
      <!-- You can add a row for taxes here if needed -->
      <div class="flex items-center justify-between border-t border-gray-200 pt-4">
        <dt class="text-base font-medium text-gray-900">{{ $t('order_summary.total') }}</dt>
        <dd class="text-base font-medium text-gray-900">€{{ grandTotal.toFixed(2) }}</dd>
      </div>
    </dl>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import { useCartStore } from '../../js/stores/cart';
import { useCheckoutStore } from '../../js/stores/checkout';
import { useI18n } from 'vue-i18n';

const cartStore = useCartStore();
const checkoutStore = useCheckoutStore();
const { t } = useI18n();

/**
 * Computes the shipping cost based on the selected delivery method.
 * @returns {number} The shipping cost.
 */
const shippingCost = computed(() => {
    return checkoutStore.deliveryMethod?.price || 0;
});

/**
 * Computes the final total by adding the cart subtotal and the shipping cost.
 * This is now fully reactive to changes in the selected delivery method.
 * @returns {number} The final total price.
 */
const grandTotal = computed(() => {
    return cartStore.subtotal + shippingCost.value;
});
</script>
