<template>
  <div class="min-h-screen">
    <!-- Hero Section with Enhanced Design -->
    <section class="relative bg-gradient-to-br from-brand-cream via-white to-brand-cream/50 overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23F5F1E8" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-6">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            Boutique en ligne
          </div>
          
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-brand-dark-brown mb-6">
            <span class="block">L'excellence des</span>
            <span class="block bg-gradient-to-r from-brand-burgundy to-brand-burgundy/80 bg-clip-text text-transparent">
              truffes françaises
            </span>
          </h1>
          
          <p class="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
            Depuis 1985, Maison Truvra sélectionne les meilleures truffes pour vous offrir une expérience gastronomique d'exception. Découvrez notre savoir-faire artisanal.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <router-link 
              to="/shop" 
              class="group relative inline-flex items-center px-8 py-4 bg-brand-burgundy text-white font-semibold rounded-xl hover:bg-brand-burgundy/90 transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
            >
              <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              Découvrir nos truffes
            </router-link>
            
            <router-link 
              to="/notre-maison" 
              class="inline-flex items-center px-8 py-4 border-2 border-brand-burgundy text-brand-burgundy font-semibold rounded-xl hover:bg-brand-burgundy hover:text-white transition-all duration-300"
            >
              Notre histoire
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Floating Elements -->
      <div class="absolute top-20 right-10 w-20 h-20 bg-brand-gold/20 rounded-full blur-xl"></div>
      <div class="absolute bottom-20 left-10 w-32 h-32 bg-brand-burgundy/10 rounded-full blur-2xl"></div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-cream text-brand-burgundy text-sm font-medium mb-4">
            Excellence
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Pourquoi choisir Maison Truvra ?
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Notre engagement pour la qualité et l'authenticité fait de nous le partenaire de confiance des plus grands chefs.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.id" class="group text-center p-8 rounded-2xl hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 text-white rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <component :is="feature.icon" class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-brand-dark-brown mb-4">{{ feature.title }}</h3>
            <p class="text-gray-600 leading-relaxed">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Products Preview -->
    <section class="py-20 bg-gradient-to-br from-gray-50 to-brand-cream/30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-4">
            Produits
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Nos produits d'exception
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez notre sélection de truffes et produits truffés, soigneusement sélectionnés pour leur qualité exceptionnelle.
          </p>
        </div>
        
        <!-- Product Grid Placeholder -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="i in 6" :key="i" class="group bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
            <div class="h-64 bg-gradient-to-br from-brand-cream to-brand-cream/50 flex items-center justify-center">
              <svg class="w-16 h-16 text-brand-burgundy/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div class="p-6">
              <h3 class="text-lg font-bold text-brand-dark-brown mb-2">Produit {{ i }}</h3>
              <p class="text-gray-600 text-sm mb-4">Description du produit exceptionnel</p>
              <div class="flex items-center justify-between">
                <span class="text-2xl font-bold text-brand-burgundy">€99</span>
                <button class="px-4 py-2 bg-brand-burgundy text-white rounded-lg hover:bg-brand-burgundy/90 transition-colors">
                  Voir
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-12">
          <router-link 
            to="/shop" 
            class="inline-flex items-center px-8 py-4 bg-brand-burgundy text-white font-semibold rounded-xl hover:bg-brand-burgundy/90 transition-all duration-300 transform hover:scale-105"
          >
            Voir tous les produits
            <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Personalized Recommendations -->
    <PersonalizedRecommendations />
    
    <!-- Recently Viewed -->
    <RecentlyViewed />

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
          <span class="block">Prêt à découvrir l'exception ?</span>
          <span class="block text-brand-cream">Commandez dès aujourd'hui.</span>
        </h2>
        <p class="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Rejoignez des milliers de clients satisfaits qui nous font confiance pour leurs besoins en truffes d'exception.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link 
            to="/shop" 
            class="inline-flex items-center px-8 py-4 bg-white text-brand-burgundy font-semibold rounded-xl hover:bg-brand-cream transition-all duration-300 transform hover:scale-105"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            Boutique
          </router-link>
          <router-link 
            to="/contact-b2c" 
            class="inline-flex items-center px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-brand-burgundy transition-all duration-300"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Nous contacter
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import PersonalizedRecommendations from '@/components/products/PersonalizedRecommendations.vue';
import RecentlyViewed from '@/components/products/RecentlyViewed.vue';

// Icons for features
import {
  ShieldCheckIcon,
  TruckIcon,
  StarIcon,
  HeartIcon,
  ClockIcon,
  GiftIcon,
} from '@heroicons/vue/outline';

const features = ref([
  {
    id: 1,
    title: 'Qualité Premium',
    description: 'Sélection rigoureuse des meilleures truffes françaises, garantissant une qualité exceptionnelle à chaque commande.',
    icon: ShieldCheckIcon,
  },
  {
    id: 2,
    title: 'Livraison Rapide',
    description: 'Expédition sous 24h pour préserver la fraîcheur et l\'arôme de nos truffes d\'exception.',
    icon: TruckIcon,
  },
  {
    id: 3,
    title: 'Savoir-faire Artisanal',
    description: 'Plus de 35 ans d\'expérience dans la sélection et la préparation des truffes les plus rares.',
    icon: StarIcon,
  },
  {
    id: 4,
    title: 'Passion Authentique',
    description: 'Une passion familiale transmise de génération en génération pour l\'excellence des truffes françaises.',
    icon: HeartIcon,
  },
  {
    id: 5,
    title: 'Fraîcheur Garantie',
    description: 'Récolte et expédition dans les 48h pour garantir la fraîcheur optimale de nos produits.',
    icon: ClockIcon,
  },
  {
    id: 6,
    title: 'Service Personnalisé',
    description: 'Conseils d\'experts et accompagnement personnalisé pour vos besoins spécifiques.',
    icon: GiftIcon,
  },
]);
</script>

<style scoped>
/* Custom animations */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}
</style>