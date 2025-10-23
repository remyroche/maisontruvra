<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-brand-burgundy via-brand-burgundy/90 to-brand-dark-brown overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-white/20 text-white text-sm font-medium mb-6">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            Espace Professionnel
          </div>
          
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
            <span class="block">Solutions B2B</span>
            <span class="block text-brand-cream">d'exception</span>
          </h1>
          
          <p class="text-xl md:text-2xl text-white/90 max-w-3xl mx-auto mb-8 leading-relaxed">
            Partenaire de confiance des restaurateurs, traiteurs et professionnels de la gastronomie. Des truffes d'exception pour vos créations culinaires.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <router-link 
              to="/pro/request-quote" 
              class="group relative inline-flex items-center px-8 py-4 bg-white text-brand-burgundy font-semibold rounded-xl hover:bg-brand-cream transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
            >
              <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Demander un devis
            </router-link>
            
            <router-link 
              to="/contact-b2b" 
              class="inline-flex items-center px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-brand-burgundy transition-all duration-300"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Nous contacter
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="stat in stats" :key="stat.id" class="text-center">
            <div class="text-4xl md:text-5xl font-bold text-brand-burgundy mb-2">{{ stat.value }}</div>
            <div class="text-gray-600 font-medium">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="py-20 bg-gradient-to-br from-gray-50 to-brand-cream/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-4">
            Services
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Nos services professionnels
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Des solutions complètes pour répondre aux besoins spécifiques des professionnels de la gastronomie.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="service in services" :key="service.id" class="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 text-white rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <component :is="service.icon" class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-brand-dark-brown mb-4">{{ service.title }}</h3>
            <p class="text-gray-600 leading-relaxed mb-6">{{ service.description }}</p>
            <ul class="space-y-2">
              <li v-for="feature in service.features" :key="feature" class="flex items-center text-sm text-gray-600">
                <svg class="w-4 h-4 text-brand-burgundy mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ feature }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Process Section -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-cream text-brand-burgundy text-sm font-medium mb-4">
            Processus
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Comment ça marche ?
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Un processus simple et transparent pour répondre à vos besoins professionnels.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div v-for="(step, index) in processSteps" :key="step.id" class="text-center relative">
            <div class="relative">
              <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 text-white rounded-full mb-6 text-xl font-bold">
                {{ index + 1 }}
              </div>
              <div v-if="index < processSteps.length - 1" class="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-gradient-to-r from-brand-burgundy to-transparent transform translate-x-8"></div>
            </div>
            <h3 class="text-lg font-bold text-brand-dark-brown mb-4">{{ step.title }}</h3>
            <p class="text-gray-600">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-20 bg-gradient-to-br from-brand-burgundy/5 to-brand-cream/30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-4">
            Témoignages
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Ils nous font confiance
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez ce que disent nos clients professionnels de nos services.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="testimonial in testimonials" :key="testimonial.id" class="bg-white rounded-2xl p-8 shadow-lg">
            <div class="flex items-center mb-6">
              <div class="flex text-brand-gold">
                <svg v-for="i in 5" :key="i" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
            </div>
            <p class="text-gray-600 italic mb-6">"{{ testimonial.content }}"</p>
            <div class="flex items-center">
              <div class="w-12 h-12 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {{ testimonial.author.charAt(0) }}
              </div>
              <div class="ml-4">
                <div class="font-semibold text-brand-dark-brown">{{ testimonial.author }}</div>
                <div class="text-sm text-gray-600">{{ testimonial.position }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
          <span class="block">Prêt à nous rejoindre ?</span>
          <span class="block text-brand-cream">Démarrez votre partenariat</span>
        </h2>
        <p class="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
          Rejoignez plus de 500 professionnels qui nous font confiance pour leurs besoins en truffes d'exception.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link 
            to="/pro/request-quote" 
            class="inline-flex items-center px-8 py-4 bg-white text-brand-burgundy font-semibold rounded-xl hover:bg-brand-cream transition-all duration-300 transform hover:scale-105"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Demander un devis
          </router-link>
          <router-link 
            to="/contact-b2b" 
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

// Icons for services
import {
  DocumentTextIcon,
  TruckIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ClockIcon,
  GiftIcon,
} from '@heroicons/vue/outline';

const stats = ref([
  { id: 1, value: '500+', label: 'Clients professionnels' },
  { id: 2, value: '35+', label: 'Années d\'expérience' },
  { id: 3, value: '24h', label: 'Délai de livraison' },
  { id: 4, value: '100%', label: 'Satisfaction client' },
]);

const services = ref([
  {
    id: 1,
    title: 'Devis personnalisés',
    description: 'Des devis sur mesure adaptés à vos besoins spécifiques et à votre volume de commande.',
    icon: DocumentTextIcon,
    features: [
      'Réponse sous 24h',
      'Prix dégressifs selon volume',
      'Conditions de paiement flexibles',
      'Suivi personnalisé'
    ]
  },
  {
    id: 2,
    title: 'Livraison express',
    description: 'Livraison rapide et sécurisée pour préserver la fraîcheur de nos truffes.',
    icon: TruckIcon,
    features: [
      'Expédition sous 24h',
      'Emballage isotherme',
      'Suivi en temps réel',
      'Livraison partout en France'
    ]
  },
  {
    id: 3,
    title: 'Support dédié',
    description: 'Un conseiller dédié pour vous accompagner dans vos projets culinaires.',
    icon: UserGroupIcon,
    features: [
      'Conseil d\'expert',
      'Accompagnement personnalisé',
      'Formation sur les truffes',
      'Support technique'
    ]
  },
  {
    id: 4,
    title: 'Qualité garantie',
    description: 'Certification et traçabilité complète de nos produits d\'exception.',
    icon: ShieldCheckIcon,
    features: [
      'Certification qualité',
      'Traçabilité complète',
      'Contrôles réguliers',
      'Garantie de fraîcheur'
    ]
  },
  {
    id: 5,
    title: 'Disponibilité 24/7',
    description: 'Service client disponible pour répondre à vos urgences culinaires.',
    icon: ClockIcon,
    features: [
      'Hotline dédiée',
      'Urgences culinaires',
      'Réponse immédiate',
      'Support technique'
    ]
  },
  {
    id: 6,
    title: 'Programmes fidélité',
    description: 'Avantages exclusifs et remises pour nos clients les plus fidèles.',
    icon: GiftIcon,
    features: [
      'Remises progressives',
      'Produits exclusifs',
      'Événements privés',
      'Accès prioritaire'
    ]
  },
]);

const processSteps = ref([
  {
    id: 1,
    title: 'Demande de devis',
    description: 'Remplissez notre formulaire en ligne ou contactez-nous directement.'
  },
  {
    id: 2,
    title: 'Étude personnalisée',
    description: 'Notre équipe étudie votre demande et vous propose une solution adaptée.'
  },
  {
    id: 3,
    title: 'Validation & commande',
    description: 'Validation du devis et passage de commande avec conditions négociées.'
  },
  {
    id: 4,
    title: 'Livraison & suivi',
    description: 'Livraison express et suivi personnalisé de votre commande.'
  },
]);

const testimonials = ref([
  {
    id: 1,
    content: "Maison Truvra est notre partenaire de confiance depuis 5 ans. La qualité de leurs truffes est exceptionnelle et leur service client irréprochable.",
    author: "Chef Michel Dubois",
    position: "Restaurant L'Étoile, Paris"
  },
  {
    id: 2,
    content: "Leur réactivité et la fraîcheur de leurs produits nous permettent de proposer des plats d'exception à nos clients. Un partenaire indispensable.",
    author: "Sophie Martin",
    position: "Traiteur Les Délices, Lyon"
  },
  {
    id: 3,
    content: "Des conseils d'experts et des produits de qualité premium. Maison Truvra a su nous accompagner dans le développement de notre carte truffée.",
    author: "Chef Pierre Moreau",
    position: "Brasserie Le Gourmet, Nice"
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