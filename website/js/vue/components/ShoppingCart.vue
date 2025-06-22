<template>
  <div class="bg-white">
    <div class="mx-auto max-w-2xl px-4 pt-16 pb-24 sm:px-6 lg:max-w-7xl lg:px-8">
      <h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl" data-i18n="cart.title">Shopping Cart</h1>
      <div v-if="cart.isLoaded && cart.items.length > 0" class="mt-12 lg:grid lg:grid-cols-12 lg:items-start lg:gap-x-12 xl:gap-x-16">
        <section aria-labelledby="cart-heading" class="lg:col-span-7">
          <h2 id="cart-heading" class="sr-only">Items in your shopping cart</h2>

          <ul role="list" class="divide-y divide-gray-200 border-t border-b border-gray-200">
            <li v-for="item in cart.items" :key="item.id" class="flex py-6 sm:py-10">
              <div class="flex-shrink-0">
                <img :src="item.product.image_url || 'https://placehold.co/200x200/e2e8f0/e2e8f0?text=Image'" :alt="item.product.name" class="h-24 w-24 rounded-md object-cover object-center sm:h-48 sm:w-48">
              </div>

              <div class="ml-4 flex flex-1 flex-col justify-between sm:ml-6">
                <div class="relative pr-9 sm:grid sm:grid-cols-2 sm:gap-x-6 sm:pr-0">
                  <div>
                    <div class="flex justify-between">
                      <h3 class="text-sm">
                        <a :href="`/produit-detail.html?id=${item.product.id}`" class="font-medium text-gray-700 hover:text-gray-800">{{ item.product.name }}</a>
                      </h3>
                    </div>
                    <!-- Product variant/options can go here -->
                    <p class="mt-1 text-sm font-medium text-gray-900">{{ formatPrice(item.price) }}</p>
                  </div>

                  <div class="mt-4 sm:mt-0 sm:pr-9">
                    <label :for="`quantity-${item.id}`" class="sr-only">Quantity, {{ item.product.name }}</label>
                    <select
                      :id="`quantity-${item.id}`"
                      :name="`quantity-${item.id}`"
                      @change="updateQuantity(item.id, $event.target.value)"
                      class="max-w-full rounded-md border border-gray-300 py-1.5 text-left text-base font-medium leading-5 text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option v-for="n in 10" :key="n" :value="n" :selected="n === item.quantity">{{ n }}</option>
                    </select>

                    <div class="absolute top-0 right-0">
                      <button @click="removeItem(item.id)" type="button" class="-m-2 inline-flex p-2 text-gray-400 hover:text-gray-500">
                        <span class="sr-only">Remove</span>
                        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Instock status can go here -->
              </div>
            </li>
          </ul>
        </section>

        <!-- Order summary -->
        <section aria-labelledby="summary-heading" class="mt-16 rounded-lg bg-gray-50 px-4 py-6 sm:p-6 lg:col-span-5 lg:mt-0 lg:p-8">
          <h2 id="summary-heading" class="text-lg font-medium text-gray-900" data-i18n="cart.summary">Order summary</h2>
          <dl class="mt-6 space-y-4">
            <div class="flex items-center justify-between">
              <dt class="text-sm text-gray-600" data-i18n="cart.subtotal">Subtotal</dt>
              <dd class="text-sm font-medium text-gray-900">{{ cart.formattedTotal }}</dd>
            </div>
            <!-- Shipping and Taxes can be added here -->
            <div class="flex items-center justify-between border-t border-gray-200 pt-4">
              <dt class="text-base font-medium text-gray-900" data-i18n="cart.orderTotal">Order total</dt>
              <dd class="text-base font-medium text-gray-900">{{ cart.formattedTotal }}</dd>
            </div>
          </dl>

          <div class="mt-6">
            <a href="/payment.html" class="w-full rounded-md border border-transparent bg-indigo-600 py-3 px-4 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-50" data-i18n="cart.checkout">Checkout</a>
          </div>
        </section>
      </div>
      <div v-else class="text-center mt-12">
          <p v-if="!cart.isLoaded" data-i18n="cart.loading">Loading your cart...</p>
          <p v-else data-i18n="cart.empty">Your cart is empty.</p>
          <div class="mt-6">
             <a href="/nos-produits.html" type="button" class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" data-i18n="cart.continueShopping">
                Continue Shopping
            </a>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCartStore } from '../stores/cart';

const cart = useCartStore();

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(price / 100);
};

const updateQuantity = async (itemId, quantity) => {
  await cart.updateItem(itemId, parseInt(quantity, 10));
};

const removeItem = async (itemId) => {
  await cart.removeItem(itemId);
};
</script>
