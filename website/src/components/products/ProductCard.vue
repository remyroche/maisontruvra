<template>
  <div class="group relative border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-shadow duration-300">
    <div class="aspect-w-1 aspect-h-1 w-full overflow-hidden bg-gray-200">
      <img :src="product.image_url || '/static/assets/placeholder.png'" :alt="product.name" class="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300" />
    </div>
    <div class="p-4 text-center">
      <h3 class="text-sm text-gray-700 font-medium">
        <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }">
          <span aria-hidden="true" class="absolute inset-0" />
          {{ product.name }}
        </router-link>
      </h3>
      <p class="mt-1 text-lg font-semibold text-gray-900">€{{ product.price.toFixed(2) }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  product: {
    type: Object,
    required: true,
  },
});
</script>