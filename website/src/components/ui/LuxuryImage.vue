<template>
  <div class="relative group overflow-hidden rounded-2xl" :class="containerClass">
    <!-- Image Container -->
    <div class="relative overflow-hidden" :class="aspectClass">
      <img
        v-if="src"
        :src="src"
        :alt="alt"
        :class="[
          'w-full h-full object-cover transition-luxury group-hover:scale-110',
          imageClass
        ]"
        loading="lazy"
      />
      
      <!-- Placeholder -->
      <div v-else class="w-full h-full bg-gradient-to-br from-brand-cream to-brand-cream/50 flex items-center justify-center">
        <div class="text-6xl opacity-30">🍄</div>
      </div>
      
      <!-- Overlay -->
      <div v-if="overlay" class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-luxury"></div>
      
      <!-- Content Overlay -->
      <div v-if="$slots.overlay" class="absolute inset-0 flex items-end p-6">
        <div class="text-white transform translate-y-4 group-hover:translate-y-0 transition-luxury">
          <slot name="overlay" />
        </div>
      </div>
    </div>
    
    <!-- Caption -->
    <div v-if="$slots.caption || caption" class="mt-4 space-y-2">
      <slot name="caption">
        <p v-if="caption" class="text-sm text-gray-600 font-medium">{{ caption }}</p>
      </slot>
    </div>
    
    <!-- Decorative Elements -->
    <div v-if="decorative" class="absolute -top-2 -right-2 w-8 h-8 bg-brand-gold/20 rounded-full blur-sm group-hover:scale-150 transition-luxury"></div>
    <div v-if="decorative" class="absolute -bottom-2 -left-2 w-12 h-12 bg-brand-burgundy/10 rounded-full blur-md group-hover:scale-125 transition-luxury"></div>
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
    default: ''
  },
  aspect: {
    type: String,
    default: 'square',
    validator: (value) => ['square', 'video', 'wide', 'tall', 'auto'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'elevated', 'floating', 'minimal'].includes(value)
  },
  overlay: {
    type: Boolean,
    default: false
  },
  decorative: {
    type: Boolean,
    default: false
  },
  caption: {
    type: String,
    default: null
  },
  containerClass: {
    type: String,
    default: ''
  },
  imageClass: {
    type: String,
    default: ''
  }
});

const aspectClass = computed(() => {
  const aspects = {
    square: 'aspect-square',
    video: 'aspect-video',
    wide: 'aspect-[16/9]',
    tall: 'aspect-[3/4]',
    auto: 'aspect-auto'
  };
  return aspects[props.aspect];
});

const containerClasses = computed(() => {
  const variants = {
    default: 'shadow-luxury',
    elevated: 'shadow-luxury-lg',
    floating: 'shadow-luxury-xl hover:shadow-luxury-2xl hover:-translate-y-2',
    minimal: 'shadow-none'
  };
  return variants[props.variant];
});
</script>