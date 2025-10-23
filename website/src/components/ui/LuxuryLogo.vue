<template>
  <div class="flex items-center space-x-3" :class="containerClass">
    <!-- Logo Icon -->
    <div class="relative">
      <div :class="[
        'flex items-center justify-center rounded-xl transition-luxury',
        sizeClasses,
        variantClasses
      ]">
        <img 
          v-if="src" 
          :src="src" 
          :alt="alt"
          :class="iconSizeClasses"
          class="object-contain"
        />
        <div v-else class="text-brand-burgundy font-bold" :class="iconSizeClasses">
          🍄
        </div>
      </div>
      
      <!-- Decorative Ring -->
      <div v-if="decorative" class="absolute -inset-2 rounded-2xl border-2 border-brand-gold/20 animate-pulse"></div>
    </div>
    
    <!-- Brand Text -->
    <div v-if="showText" class="space-y-1">
      <div class="text-xs font-medium text-gray-500 uppercase tracking-wider" v-if="subtitle">
        {{ subtitle }}
      </div>
      <div class="font-bold text-brand-dark-brown" :class="textSizeClasses">
        {{ brandName }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  src: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: 'Logo'
  },
  brandName: {
    type: String,
    default: 'Maison Truvra'
  },
  subtitle: {
    type: String,
    default: null
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'minimal', 'elevated', 'gradient'].includes(value)
  },
  showText: {
    type: Boolean,
    default: true
  },
  decorative: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  }
});

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20'
  };
  return sizes[props.size];
});

const iconSizeClasses = computed(() => {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };
  return sizes[props.size];
});

const textSizeClasses = computed(() => {
  const sizes = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-xl',
    xl: 'text-2xl'
  };
  return sizes[props.size];
});

const variantClasses = computed(() => {
  const variants = {
    default: 'bg-white shadow-luxury border-luxury',
    minimal: 'bg-transparent',
    elevated: 'bg-white shadow-luxury-lg border-luxury',
    gradient: 'bg-gradient-to-br from-brand-cream to-white shadow-luxury border-luxury'
  };
  return variants[props.variant];
});
</script>