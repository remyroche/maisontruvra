<template>
  <div class="space-y-6">
    <!-- Welcome Section -->
    <div class="bg-gradient-to-r from-brand-burgundy to-brand-burgundy/90 rounded-lg p-6 text-white">
      <h1 class="text-2xl font-bold mb-2">Bienvenue dans votre espace professionnel</h1>
      <p class="text-brand-cream">Accédez à vos commandes, demandes de devis et services B2B</p>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Devis en attente</p>
            <p class="text-2xl font-bold text-gray-900">{{ pendingQuotes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Commandes actives</p>
            <p class="text-2xl font-bold text-gray-900">{{ activeOrders }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Chiffre d'affaires</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(totalRevenue) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <router-link 
          to="/pro/request-quote" 
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-brand-burgundy hover:bg-brand-cream/20 transition-colors"
        >
          <div class="p-2 bg-brand-burgundy/10 rounded-lg mr-3">
            <svg class="w-5 h-5 text-brand-burgundy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900">Demander un devis</p>
            <p class="text-sm text-gray-600">Nouvelle demande</p>
          </div>
        </router-link>

        <router-link 
          to="/pro/my-quotes" 
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-brand-burgundy hover:bg-brand-cream/20 transition-colors"
        >
          <div class="p-2 bg-brand-burgundy/10 rounded-lg mr-3">
            <svg class="w-5 h-5 text-brand-burgundy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900">Mes devis</p>
            <p class="text-sm text-gray-600">Voir l'historique</p>
          </div>
        </router-link>

        <router-link 
          to="/pro/orders" 
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-brand-burgundy hover:bg-brand-cream/20 transition-colors"
        >
          <div class="p-2 bg-brand-burgundy/10 rounded-lg mr-3">
            <svg class="w-5 h-5 text-brand-burgundy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900">Mes commandes</p>
            <p class="text-sm text-gray-600">Suivre les commandes</p>
          </div>
        </router-link>

        <router-link 
          to="/contact-b2b" 
          class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-brand-burgundy hover:bg-brand-cream/20 transition-colors"
        >
          <div class="p-2 bg-brand-burgundy/10 rounded-lg mr-3">
            <svg class="w-5 h-5 text-brand-burgundy" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900">Support B2B</p>
            <p class="text-sm text-gray-600">Nous contacter</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Activité récente</h2>
      <div class="space-y-4">
        <div v-for="activity in recentActivities" :key="activity.id" class="flex items-center p-4 bg-gray-50 rounded-lg">
          <div class="p-2 bg-white rounded-full mr-4">
            <component :is="activity.icon" class="w-5 h-5 text-brand-burgundy" />
          </div>
          <div class="flex-1">
            <p class="font-medium text-gray-900">{{ activity.title }}</p>
            <p class="text-sm text-gray-600">{{ activity.description }}</p>
          </div>
          <div class="text-sm text-gray-500">{{ activity.date }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useB2BStore } from '@/stores/b2b';
import { useCurrencyFormatter } from '@/composables/useCurrencyFormatter';

// Icons for recent activities
import {
  DocumentTextIcon,
  ShoppingBagIcon,
  ChatAlt2Icon,
  CheckCircleIcon,
} from '@heroicons/vue/outline';

const b2bStore = useB2BStore();
const { formatCurrency } = useCurrencyFormatter();

// Data
const pendingQuotes = ref(0);
const activeOrders = ref(0);
const totalRevenue = ref(0);

const recentActivities = ref([
  {
    id: 1,
    title: 'Nouveau devis soumis',
    description: 'Demande de devis pour 50kg de truffes noires',
    date: 'Il y a 2 heures',
    icon: DocumentTextIcon,
  },
  {
    id: 2,
    title: 'Commande confirmée',
    description: 'Commande #12345 - 25kg de truffes blanches',
    date: 'Il y a 1 jour',
    icon: ShoppingBagIcon,
  },
  {
    id: 3,
    title: 'Réponse reçue',
    description: 'Réponse à votre demande de devis #789',
    date: 'Il y a 2 jours',
    icon: ChatAlt2Icon,
  },
  {
    id: 4,
    title: 'Commande livrée',
    description: 'Commande #12340 livrée avec succès',
    date: 'Il y a 3 jours',
    icon: CheckCircleIcon,
  },
]);

// Load B2B data
onMounted(async () => {
  try {
    // Load B2B dashboard data
    await b2bStore.loadDashboardData();
    
    // Update stats (these would come from the store)
    pendingQuotes.value = b2bStore.pendingQuotes || 0;
    activeOrders.value = b2bStore.activeOrders || 0;
    totalRevenue.value = b2bStore.totalRevenue || 0;
  } catch (error) {
    console.error('Error loading B2B dashboard data:', error);
  }
});
</script>