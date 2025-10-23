<template>
  <nav class="flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2">
      <li v-for="(item, index) in breadcrumbs" :key="index" class="flex items-center">
        <router-link
          v-if="item.to && index < breadcrumbs.length - 1"
          :to="item.to"
          class="text-gray-500 hover:text-brand-burgundy transition-colors"
        >
          {{ item.label }}
        </router-link>
        <span v-else-if="index === breadcrumbs.length - 1" class="text-brand-dark-brown font-medium">
          {{ item.label }}
        </span>
        <span v-else class="text-gray-500">
          {{ item.label }}
        </span>
        
        <svg
          v-if="index < breadcrumbs.length - 1"
          class="w-4 h-4 text-gray-400 mx-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const props = defineProps({
  customBreadcrumbs: {
    type: Array,
    default: () => []
  }
});

const route = useRoute();

const breadcrumbs = computed(() => {
  if (props.customBreadcrumbs.length > 0) {
    return props.customBreadcrumbs;
  }
  
  return generateBreadcrumbsFromRoute(route);
});

const generateBreadcrumbsFromRoute = (currentRoute) => {
  const breadcrumbs = [];
  const pathSegments = currentRoute.path.split('/').filter(segment => segment);
  
  // Add home breadcrumb
  breadcrumbs.push({
    label: 'Accueil',
    to: '/'
  });
  
  // Generate breadcrumbs from path segments
  let currentPath = '';
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    
    // Skip certain segments
    if (['admin', 'pro', 'account'].includes(segment)) {
      return;
    }
    
    const label = getLabelFromSegment(segment, currentRoute);
    const isLast = index === pathSegments.length - 1;
    
    breadcrumbs.push({
      label,
      to: isLast ? null : currentPath
    });
  });
  
  return breadcrumbs;
};

const getLabelFromSegment = (segment, currentRoute) => {
  // Handle special cases
  const specialLabels = {
    'b2c': 'Boutique',
    'b2b': 'Professionnels',
    'admin': 'Administration',
    'shop': 'Boutique',
    'le-journal': 'Journal',
    'notre-maison': 'À propos',
    'professionnels': 'Professionnels',
    'dashboard': 'Tableau de bord',
    'products': 'Produits',
    'orders': 'Commandes',
    'users': 'Utilisateurs',
    'settings': 'Paramètres'
  };
  
  if (specialLabels[segment]) {
    return specialLabels[segment];
  }
  
  // Handle dynamic segments (like product IDs)
  if (currentRoute.params.id) {
    return `Produit ${currentRoute.params.id}`;
  }
  
  // Default: capitalize first letter
  return segment.charAt(0).toUpperCase() + segment.slice(1);
};
</script>