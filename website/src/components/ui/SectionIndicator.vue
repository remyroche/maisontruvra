<template>
  <div class="fixed top-20 right-4 z-40 hidden lg:block">
    <div class="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-2">
      <div class="space-y-2">
        <button
          v-for="section in sections"
          :key="section.id"
          @click="switchToSection(section.id)"
          :class="[
            'w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 group relative',
            currentSection === section.id 
              ? 'bg-brand-burgundy text-white shadow-lg' 
              : 'text-gray-600 hover:text-brand-burgundy hover:bg-brand-cream/50'
          ]"
          :title="section.name"
        >
          <component :is="section.icon" class="w-5 h-5" />
          
          <!-- Tooltip -->
          <div class="absolute right-full mr-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            {{ section.name }}
            <div class="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-l-4 border-l-gray-900 border-t-4 border-t-transparent border-b-4 border-b-transparent"></div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// Icons
import {
  ShoppingBagIcon,
  BuildingOfficeIcon,
  CogIcon,
} from '@heroicons/vue/outline';

const router = useRouter();

const props = defineProps({
  currentSection: {
    type: String,
    default: 'b2c'
  }
});

const sections = ref([
  {
    id: 'b2c',
    name: 'Boutique',
    icon: ShoppingBagIcon,
    path: '/b2c'
  },
  {
    id: 'b2b',
    name: 'Professionnels',
    icon: BuildingOfficeIcon,
    path: '/b2b'
  },
  {
    id: 'admin',
    name: 'Administration',
    icon: CogIcon,
    path: '/admin'
  }
]);

const switchToSection = (sectionId) => {
  const section = sections.value.find(s => s.id === sectionId);
  if (section) {
    router.push(section.path);
  }
};
</script>