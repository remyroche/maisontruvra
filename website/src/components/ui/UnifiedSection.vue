<template>
  <section 
    :class="[
      'py-20',
      backgroundVariant === 'white' ? 'bg-white' : '',
      backgroundVariant === 'gray' ? 'bg-gray-50' : '',
      backgroundVariant === 'gradient' ? 'bg-gradient-to-br from-brand-cream/30 to-white' : '',
      backgroundVariant === 'dark' ? 'bg-gradient-to-br from-gray-900 to-brand-dark-brown' : '',
      backgroundVariant === 'brand' ? 'bg-gradient-to-br from-brand-burgundy to-brand-burgundy/90' : '',
      className
    ]"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section Header -->
      <div v-if="showHeader" class="text-center mb-16">
        <div v-if="badge" class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-4" :class="badgeClasses">
          {{ badge }}
        </div>
        
        <h2 v-if="title" :class="titleClasses">
          {{ title }}
        </h2>
        
        <p v-if="subtitle" :class="subtitleClasses">
          {{ subtitle }}
        </p>
      </div>
      
      <!-- Section Content -->
      <div :class="contentClasses">
        <slot />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  badge: {
    type: String,
    default: ''
  },
  backgroundVariant: {
    type: String,
    default: 'white',
    validator: (value) => ['white', 'gray', 'gradient', 'dark', 'brand'].includes(value)
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  contentClass: {
    type: String,
    default: ''
  },
  className: {
    type: String,
    default: ''
  }
});

const badgeClasses = computed(() => {
  const variants = {
    white: 'bg-brand-cream text-brand-burgundy',
    gray: 'bg-brand-burgundy/10 text-brand-burgundy',
    gradient: 'bg-brand-cream text-brand-burgundy',
    dark: 'bg-brand-burgundy/20 text-brand-cream',
    brand: 'bg-white/20 text-white'
  };
  return variants[props.backgroundVariant];
});

const titleClasses = computed(() => {
  const base = 'text-4xl md:text-5xl font-bold mb-6';
  const colors = {
    white: 'text-brand-dark-brown',
    gray: 'text-brand-dark-brown',
    gradient: 'text-brand-dark-brown',
    dark: 'text-white',
    brand: 'text-white'
  };
  return `${base} ${colors[props.backgroundVariant]}`;
});

const subtitleClasses = computed(() => {
  const base = 'text-xl max-w-3xl mx-auto';
  const colors = {
    white: 'text-gray-600',
    gray: 'text-gray-600',
    gradient: 'text-gray-600',
    dark: 'text-white/90',
    brand: 'text-white/90'
  };
  return `${base} ${colors[props.backgroundVariant]}`;
});

const contentClasses = computed(() => {
  return props.contentClass || '';
});
</script>