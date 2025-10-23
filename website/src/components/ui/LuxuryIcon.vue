<template>
  <div 
    :class="[
      'inline-flex items-center justify-center transition-luxury',
      sizeClasses,
      variantClasses,
      containerClass
    ]"
  >
    <component 
      :is="icon" 
      :class="[
        'transition-luxury',
        iconSizeClasses,
        iconClass
      ]"
    />
    
    <!-- Decorative Background -->
    <div v-if="decorative" class="absolute inset-0 rounded-full bg-gradient-to-br from-brand-gold/10 to-brand-burgundy/10 animate-pulse"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  icon: {
    type: [String, Object],
    required: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'secondary', 'minimal', 'elevated'].includes(value)
  },
  decorative: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  },
  iconClass: {
    type: String,
    default: ''
  }
});

const sizeClasses = computed(() => {
  const sizes = {
    xs: 'w-4 h-4',
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };
  return sizes[props.size];
});

const iconSizeClasses = computed(() => {
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8'
  };
  return sizes[props.size];
});

const variantClasses = computed(() => {
  const variants = {
    default: 'text-gray-600',
    primary: 'text-brand-burgundy',
    secondary: 'text-brand-gold',
    minimal: 'text-gray-400',
    elevated: 'text-brand-burgundy bg-white shadow-luxury rounded-lg'
  };
  return variants[props.variant];
});
</script>