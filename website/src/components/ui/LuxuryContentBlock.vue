<template>
  <section :class="[
    'relative overflow-hidden',
    backgroundClass,
    containerClass
  ]">
    <!-- Background Pattern -->
    <div v-if="pattern" class="absolute inset-0 opacity-10" :class="patternClass"></div>
    
    <!-- Content Container -->
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" :class="paddingClass">
      <!-- Header Section -->
      <div v-if="$slots.header || title" class="mb-16" :class="headerAlignment">
        <slot name="header">
          <div v-if="badge" class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6" :class="badgeClass">
            {{ badge }}
          </div>
          <h2 v-if="title" class="text-4xl md:text-5xl lg:text-6xl font-bold mb-6" :class="titleClass">
            {{ title }}
          </h2>
          <p v-if="subtitle" class="text-lg md:text-xl text-gray-600 leading-relaxed max-w-3xl" :class="subtitleAlignment">
            {{ subtitle }}
          </p>
        </slot>
      </div>
      
      <!-- Main Content -->
      <div :class="contentLayout">
        <slot />
      </div>
      
      <!-- Footer Section -->
      <div v-if="$slots.footer" class="mt-16" :class="footerAlignment">
        <slot name="footer" />
      </div>
    </div>
    
    <!-- Decorative Elements -->
    <div v-if="decorative" class="absolute top-10 right-10 w-32 h-32 bg-brand-gold/5 rounded-full blur-3xl"></div>
    <div v-if="decorative" class="absolute bottom-10 left-10 w-48 h-48 bg-brand-burgundy/5 rounded-full blur-3xl"></div>
  </section>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: null
  },
  subtitle: {
    type: String,
    default: null
  },
  badge: {
    type: String,
    default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'dark', 'gradient', 'minimal'].includes(value)
  },
  layout: {
    type: String,
    default: 'centered',
    validator: (value) => ['centered', 'left', 'right', 'asymmetrical'].includes(value)
  },
  padding: {
    type: String,
    default: 'lg',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  },
  pattern: {
    type: Boolean,
    default: false
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

const backgroundClass = computed(() => {
  const variants = {
    default: 'bg-white',
    dark: 'bg-gray-900 text-white',
    gradient: 'bg-gradient-to-br from-brand-cream via-white to-brand-cream/30',
    minimal: 'bg-transparent'
  };
  return variants[props.variant];
});

const paddingClass = computed(() => {
  const paddings = {
    sm: 'py-12',
    md: 'py-16',
    lg: 'py-20',
    xl: 'py-24',
    '2xl': 'py-32'
  };
  return paddings[props.padding];
});

const headerAlignment = computed(() => {
  const alignments = {
    centered: 'text-center',
    left: 'text-left',
    right: 'text-right',
    asymmetrical: 'text-left lg:text-right'
  };
  return alignments[props.layout];
});

const subtitleAlignment = computed(() => {
  const alignments = {
    centered: 'mx-auto',
    left: 'mr-auto',
    right: 'ml-auto',
    asymmetrical: 'mr-auto lg:ml-auto'
  };
  return alignments[props.layout];
});

const footerAlignment = computed(() => {
  const alignments = {
    centered: 'text-center',
    left: 'text-left',
    right: 'text-right',
    asymmetrical: 'text-left lg:text-right'
  };
  return alignments[props.layout];
});

const contentLayout = computed(() => {
  const layouts = {
    centered: 'flex flex-col items-center',
    left: 'flex flex-col items-start',
    right: 'flex flex-col items-end',
    asymmetrical: 'grid lg:grid-cols-12 gap-12 items-center'
  };
  return layouts[props.layout];
});

const badgeClass = computed(() => {
  const variants = {
    default: 'bg-brand-cream text-brand-burgundy',
    dark: 'bg-white/10 text-white',
    gradient: 'bg-brand-burgundy/10 text-brand-burgundy',
    minimal: 'bg-gray-100 text-gray-600'
  };
  return variants[props.variant];
});

const titleClass = computed(() => {
  const variants = {
    default: 'text-brand-dark-brown',
    dark: 'text-white',
    gradient: 'text-brand-dark-brown',
    minimal: 'text-gray-900'
  };
  return variants[props.variant];
});

const patternClass = computed(() => {
  return 'bg-[url("data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23F5F1E8\' fill-opacity=\'0.3\'%3E%3Cpath d=\'M20 20c0-11.046-8.954-20-20-20v20h20z\'/%3E%3C/g%3E%3C/svg%3E")]';
});
</script>