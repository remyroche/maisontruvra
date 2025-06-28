<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Mon Compte</h1>

    <div v-if="isLoading" class="text-center">
      <p>Loading...</p>
    </div>

    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <div v-if="user" class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Left Column: Navigation -->
      <div class="md:col-span-1">
        <div class="bg-white p-6 rounded-lg shadow">
          <ul class="space-y-4">
            <li>
              <a href="#" @click.prevent="activeTab = 'profile'" :class="['block font-medium', activeTab === 'profile' ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600']">
                Mon Profil
              </a>
            </li>
            <li>
              <a href="#" @click.prevent="activeTab = 'orders'" :class="['block font-medium', activeTab === 'orders' ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600']">
                Mes Commandes
              </a>
            </li>
            <li>
              <a href="#" @click.prevent="activeTab = 'addresses'" :class="['block font-medium', activeTab === 'addresses' ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600']">
                Mes Adresses
              </a>
            </li>
             <li>
              <a href="#" @click.prevent="activeTab = 'danger'" :class="['block font-medium', activeTab === 'danger' ? 'text-red-600' : 'text-gray-700 hover:text-red-600']">
                Zone de Danger
              </a>
            </li>
            <li>
              <button @click="handleLogout" class="w-full text-left font-medium text-gray-700 hover:text-blue-600">
                Déconnexion
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Right Column: Content -->
      <div class="md:col-span-2">
        <!-- Profile Section -->
        <div v-if="activeTab === 'profile'" class="bg-white p-8 rounded-lg shadow">
          <h2 class="text-2xl font-semibold mb-4">Informations Personnelles</h2>
          <form @submit.prevent="updateProfile">
            <div class="mb-4">
              <label for="firstName" class="block text-sm font-medium text-gray-700">Prénom</label>
              <input type="text" id="firstName" v-model="editableUser.first_name" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="mb-4">
              <label for="lastName" class="block text-sm font-medium text-gray-700">Nom</label>
              <input type="text" id="lastName" v-model="editableUser.last_name" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div class="mb-4">
              <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
              <input type="email" id="email" :value="user.email" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-100" disabled>
            </div>
            <button type="submit" class="bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Mettre à jour
            </button>
          </form>
        </div>

        <!-- Orders Section -->
        <div v-if="activeTab === 'orders'" class="bg-white p-8 rounded-lg shadow">
          <h2 class="text-2xl font-semibold mb-4">Historique des Commandes</h2>
          <div v-if="orders.length > 0" class="space-y-4">
            <div v-for="order in orders" :key="order.id" class="border p-4 rounded-md">
              <p><strong>Commande #{{ order.id }}</strong> - {{ order.status }}</p>
              <p>Date: {{ new Date(order.created_at).toLocaleDateString() }}</p>
              <p>Total: {{ order.total_amount }} €</p>
            </div>
          </div>
          <p v-else>Vous n'avez aucune commande.</p>
        </div>

        <!-- Addresses Section -->
        <div v-if="activeTab === 'addresses'" class="bg-white p-8 rounded-lg shadow">
          <h2 class="text-2xl font-semibold mb-4">Mes Adresses</h2>
           <div v-if="addresses.length > 0" class="space-y-4">
               <div v-for="address in addresses" :key="address.id" class="border p-4 rounded-md">
                   <p>{{ address.address_line_1 }}</p>
                   <p v-if="address.address_line_2">{{ address.address_line_2 }}</p>
                   <p>{{ address.city }}, {{ address.postal_code }}</p>
                   <p>{{ address.country }}</p>
               </div>
           </div>
          <p v-else>Vous n'avez aucune adresse enregistrée.</p>
        </div>
        
        <!-- Danger Zone -->
        <div v-if="activeTab === 'danger'" class="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg shadow-md">
            <h2 class="text-2xl font-semibold text-red-800 mb-4">Zone de Danger</h2>
            <p class="text-red-700 mb-4">La suppression de votre compte est permanente et ne peut être annulée. Toutes vos données, y compris l'historique des commandes et les informations personnelles, seront définitivement effacées.</p>
            <button @click="deleteAccount" class="bg-red-600 text-white font-bold py-2 px-4 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                Supprimer mon compte
            </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

// State for the active tab
const activeTab = ref('profile');

// Access the user store and router
const userStore = useUserStore();
const router = useRouter();

// Computed properties to get data from the store
const user = computed(() => userStore.user);
const orders = computed(() => userStore.orders);
const addresses = computed(() => userStore.addresses);
const isLoading = computed(() => userStore.isLoading);
const error = computed(() => userStore.error);

// Local state for the editable user profile
const editableUser = ref({
  first_name: '',
  last_name: ''
});

// Watch for changes in the user data from the store to update the local form
watch(user, (newUser) => {
  if (newUser) {
    editableUser.value.first_name = newUser.first_name;
    editableUser.value.last_name = newUser.last_name;
  }
}, { immediate: true });


// Fetch user data when the component is mounted
onMounted(() => {
  userStore.fetchUserProfile();
  userStore.fetchUserOrders();
  userStore.fetchUserAddresses();
});

// Method to handle profile updates
const updateProfile = async () => {
  await userStore.updateUserProfile(editableUser.value);
};

// Method to handle logout
const handleLogout = async () => {
  await userStore.logout();
  router.push('/'); // Redirect to homepage after logout
};

// Method to handle account deletion
const deleteAccount = async () => {
  if (confirm("Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.")) {
    await userStore.deleteAccount();
    router.push('/'); // Redirect to homepage after deletion
  }
};
</script>

<style scoped>
/* Scoped styles can be added here if needed */
</style>
