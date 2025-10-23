<template>
  <div 
    :class="[
      'rounded-2xl transition-luxury',
      hoverEffect ? 'hover-lift hover-glow' : '',
      variant === 'elevated' ? 'bg-white shadow-luxury-lg border-luxury' : 'bg-white shadow-luxury border-luxury',
      variant === 'gradient' ? 'bg-gradient-to-br from-white to-brand-cream/30 shadow-luxury border-luxury' : '',
      variant === 'dark' ? 'bg-gray-800 text-white shadow-luxury-xl border border-gray-700' : '',
      size === 'sm' ? 'p-4' : size === 'lg' ? 'p-8' : 'p-6',
      className
    ]"
  >
    <div v-if="$slots.header" class="mb-6">
      <slot name="header" />
    </div>
    
    <div :class="contentClass">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="mt-6 pt-6 border-t border-gray-200">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'elevated', 'gradient', 'dark'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  hoverEffect: {
    type: Boolean,
    default: true
  },
  className: {
    type: String,
    default: ''
  }
});

const contentClass = computed(() => {
  const base = 'space-y-4';
  return base;
});
</script>