<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-gray-900 via-brand-dark-brown to-gray-800 overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="text-center">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/20 text-brand-cream text-sm font-medium mb-6">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Administration
          </div>
          
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
            <span class="block">Tableau de bord</span>
            <span class="block text-brand-cream">Administrateur</span>
          </h1>
          
          <p class="text-xl md:text-2xl text-white/90 max-w-3xl mx-auto mb-8 leading-relaxed">
            Gérez efficacement votre boutique, vos produits, vos clients et vos commandes avec notre interface d'administration complète.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <router-link 
              to="/admin/products" 
              class="group relative inline-flex items-center px-8 py-4 bg-brand-burgundy text-white font-semibold rounded-xl hover:bg-brand-burgundy/90 transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
            >
              <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              Gérer les produits
            </router-link>
            
            <router-link 
              to="/admin/orders" 
              class="inline-flex items-center px-8 py-4 border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-brand-burgundy transition-all duration-300"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              Voir les commandes
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Stats -->
    <section class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div v-for="stat in quickStats" :key="stat.id" class="text-center p-6 bg-gradient-to-br from-brand-cream/30 to-white rounded-2xl shadow-lg">
            <div class="text-4xl md:text-5xl font-bold text-brand-burgundy mb-2">{{ stat.value }}</div>
            <div class="text-gray-600 font-medium">{{ stat.label }}</div>
            <div class="text-sm text-gray-500 mt-1">{{ stat.change }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Management Modules -->
    <section class="py-20 bg-gradient-to-br from-gray-50 to-brand-cream/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-4">
            Modules
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Modules de gestion
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Accédez à tous les outils nécessaires pour gérer efficacement votre boutique en ligne.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="module in managementModules" :key="module.id" class="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 text-white rounded-2xl mb-6 group-hover:scale-110 transition-transform">
              <component :is="module.icon" class="w-8 h-8" />
            </div>
            <h3 class="text-xl font-bold text-brand-dark-brown mb-4">{{ module.title }}</h3>
            <p class="text-gray-600 leading-relaxed mb-6">{{ module.description }}</p>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-500">{{ module.items }} éléments</span>
              <router-link 
                :to="module.link" 
                class="inline-flex items-center text-brand-burgundy hover:text-brand-burgundy/80 font-medium transition-colors"
              >
                Accéder
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Activity -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-cream text-brand-burgundy text-sm font-medium mb-4">
            Activité
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Activité récente
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Suivez les dernières activités de votre boutique en temps réel.
          </p>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Recent Orders -->
          <div class="bg-white rounded-2xl shadow-lg p-8">
            <h3 class="text-xl font-bold text-brand-dark-brown mb-6 flex items-center">
              <svg class="w-6 h-6 text-brand-burgundy mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              Commandes récentes
            </h3>
            <div class="space-y-4">
              <div v-for="order in recentOrders" :key="order.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div class="font-medium text-brand-dark-brown">Commande #{{ order.id }}</div>
                  <div class="text-sm text-gray-600">{{ order.customer }}</div>
                </div>
                <div class="text-right">
                  <div class="font-semibold text-brand-burgundy">{{ order.amount }}</div>
                  <div class="text-sm text-gray-500">{{ order.date }}</div>
                </div>
              </div>
            </div>
            <div class="mt-6">
              <router-link 
                to="/admin/orders" 
                class="inline-flex items-center text-brand-burgundy hover:text-brand-burgundy/80 font-medium transition-colors"
              >
                Voir toutes les commandes
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </div>
          </div>

          <!-- System Alerts -->
          <div class="bg-white rounded-2xl shadow-lg p-8">
            <h3 class="text-xl font-bold text-brand-dark-brown mb-6 flex items-center">
              <svg class="w-6 h-6 text-brand-burgundy mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Alertes système
            </h3>
            <div class="space-y-4">
              <div v-for="alert in systemAlerts" :key="alert.id" class="flex items-start p-4 rounded-lg" :class="alert.type === 'warning' ? 'bg-yellow-50 border-l-4 border-yellow-400' : 'bg-green-50 border-l-4 border-green-400'">
                <div class="flex-shrink-0">
                  <svg v-if="alert.type === 'warning'" class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <svg v-else class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-3">
                  <div class="font-medium text-brand-dark-brown">{{ alert.title }}</div>
                  <div class="text-sm text-gray-600">{{ alert.message }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="py-20 bg-gradient-to-br from-brand-burgundy/5 to-brand-cream/30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <div class="inline-flex items-center px-4 py-2 rounded-full bg-brand-burgundy/10 text-brand-burgundy text-sm font-medium mb-4">
            Actions
          </div>
          <h2 class="text-4xl md:text-5xl font-bold text-brand-dark-brown mb-6">
            Actions rapides
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Accédez rapidement aux fonctions les plus utilisées de votre administration.
          </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <router-link 
            v-for="action in quickActions" 
            :key="action.id"
            :to="action.link"
            class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2 text-center"
          >
            <div class="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-brand-burgundy to-brand-burgundy/80 text-white rounded-xl mb-4 group-hover:scale-110 transition-transform">
              <component :is="action.icon" class="w-6 h-6" />
            </div>
            <h3 class="font-bold text-brand-dark-brown mb-2">{{ action.title }}</h3>
            <p class="text-sm text-gray-600">{{ action.description }}</p>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Icons for modules and actions
import {
  CubeIcon,
  UsersIcon,
  ShoppingBagIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/vue/outline';

const quickStats = ref([
  { id: 1, value: '1,250', label: 'Utilisateurs', change: '+12% ce mois' },
  { id: 2, value: '45', label: 'Produits', change: '+3 nouveaux' },
  { id: 3, value: '89', label: 'Commandes', change: '+8% cette semaine' },
  { id: 4, value: '€125K', label: 'Revenus', change: '+15% ce mois' },
]);

const managementModules = ref([
  {
    id: 1,
    title: 'Gestion des produits',
    description: 'Ajoutez, modifiez et gérez votre catalogue de produits avec des outils avancés.',
    icon: CubeIcon,
    items: '45 produits',
    link: '/admin/products'
  },
  {
    id: 2,
    title: 'Gestion des utilisateurs',
    description: 'Administrez les comptes clients et les permissions d\'accès.',
    icon: UsersIcon,
    items: '1,250 utilisateurs',
    link: '/admin/users'
  },
  {
    id: 3,
    title: 'Gestion des commandes',
    description: 'Suivez et traitez toutes les commandes de votre boutique.',
    icon: ShoppingBagIcon,
    items: '89 commandes',
    link: '/admin/orders'
  },
  {
    id: 4,
    title: 'Rapports et analyses',
    description: 'Analysez les performances de votre boutique avec des tableaux de bord détaillés.',
    icon: ChartBarIcon,
    items: '12 rapports',
    link: '/admin/analytics'
  },
  {
    id: 5,
    title: 'Paramètres du site',
    description: 'Configurez les paramètres généraux et l\'apparence de votre boutique.',
    icon: CogIcon,
    items: '25 paramètres',
    link: '/admin/site-settings'
  },
  {
    id: 6,
    title: 'Gestion du contenu',
    description: 'Gérez les articles de blog, les pages et le contenu marketing.',
    icon: DocumentTextIcon,
    items: '18 articles',
    link: '/admin/blog'
  },
]);

const recentOrders = ref([
  { id: 12345, customer: 'Jean Dupont', amount: '€299', date: 'Il y a 2h' },
  { id: 12344, customer: 'Marie Martin', amount: '€150', date: 'Il y a 4h' },
  { id: 12343, customer: 'Pierre Durand', amount: '€450', date: 'Il y a 6h' },
  { id: 12342, customer: 'Sophie Bernard', amount: '€200', date: 'Il y a 8h' },
]);

const systemAlerts = ref([
  {
    id: 1,
    type: 'warning',
    title: 'Stock faible',
    message: '3 produits ont un stock inférieur à 10 unités'
  },
  {
    id: 2,
    type: 'success',
    title: 'Sauvegarde réussie',
    message: 'La sauvegarde automatique s\'est terminée avec succès'
  },
  {
    id: 3,
    type: 'warning',
    title: 'Commande en attente',
    message: '5 commandes nécessitent votre attention'
  },
]);

const quickActions = ref([
  {
    id: 1,
    title: 'Nouveau produit',
    description: 'Ajouter un produit',
    icon: PlusIcon,
    link: '/admin/products?action=create'
  },
  {
    id: 2,
    title: 'Voir les commandes',
    description: 'Commandes en cours',
    icon: EyeIcon,
    link: '/admin/orders'
  },
  {
    id: 3,
    title: 'Modifier le site',
    description: 'Paramètres généraux',
    icon: PencilIcon,
    link: '/admin/site-settings'
  },
  {
    id: 4,
    title: 'Corbeille',
    description: 'Éléments supprimés',
    icon: TrashIcon,
    link: '/admin/recycling-bin'
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