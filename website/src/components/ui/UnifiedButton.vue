<template>
  <component
    :is="tag"
    :to="to"
    :href="href"
    :type="type"
    :disabled="disabled"
    :class="[
      'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300',
      sizeClasses,
      variantClasses,
      disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      hoverEffect ? 'transform hover:scale-105' : '',
      className
    ]"
    @click="handleClick"
  >
    <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <component v-if="icon && !loading" :is="icon" :class="iconClasses" />
    
    <span v-if="$slots.default" :class="textClasses">
      <slot />
    </span>
  </component>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'success'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  tag: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'a', 'router-link'].includes(value)
  },
  to: {
    type: [String, Object],
    default: null
  },
  href: {
    type: String,
    default: null
  },
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  icon: {
    type: [String, Object],
    default: null
  },
  iconPosition: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value)
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

const emit = defineEmits(['click']);

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
    xl: 'px-10 py-5 text-xl'
  };
  return sizes[props.size];
});

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-brand-burgundy text-white hover:bg-brand-burgundy/90 shadow-lg hover:shadow-xl',
    secondary: 'bg-brand-cream text-brand-burgundy hover:bg-brand-cream/80 border border-brand-burgundy/20',
    outline: 'border-2 border-brand-burgundy text-brand-burgundy hover:bg-brand-burgundy hover:text-white',
    ghost: 'text-brand-burgundy hover:bg-brand-burgundy/10',
    danger: 'bg-red-500 text-white hover:bg-red-600 shadow-lg hover:shadow-xl',
    success: 'bg-green-500 text-white hover:bg-green-600 shadow-lg hover:shadow-xl'
  };
  return variants[props.variant];
});

const iconClasses = computed(() => {
  const base = 'w-5 h-5';
  const position = props.iconPosition === 'right' ? 'ml-2' : 'mr-2';
  return `${base} ${position}`;
});

const textClasses = computed(() => {
  return props.iconPosition === 'right' ? 'order-first' : '';
});

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>