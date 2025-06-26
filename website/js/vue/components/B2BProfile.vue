<template>
  <div>
    <h2 class="text-3xl font-serif text-truffle-burgundy mb-6">Mon Profil Professionnel</h2>
    <div v-if="isLoading" class="text-center">Chargement du profil...</div>
    <div v-else-if="profile">
      <form @submit.prevent="handleUpdateProfile">
        <!-- User Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-cream rounded-lg shadow">
            <h3 class="col-span-full text-xl font-serif text-dark-brown border-b border-gold pb-2">Informations Utilisateur</h3>
            <div>
                <label for="firstName" class="block text-sm font-medium text-dark-brown">Prénom</label>
                <input type="text" v-model="profileData.first_name" id="firstName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
            <div>
                <label for="lastName" class="block text-sm font-medium text-dark-brown">Nom</label>
                <input type="text" v-model="profileData.last_name" id="lastName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
              <div>
                <label for="email" class="block text-sm font-medium text-dark-brown">Email</label>
                <input type="email" v-model="profileData.email" id="email" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
        </div>
        
        <!-- Company Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-cream rounded-lg shadow mt-8">
            <h3 class="col-span-full text-xl font-serif text-dark-brown border-b border-gold pb-2">Informations de l'Entreprise</h3>
            <div>
                <label for="companyName" class="block text-sm font-medium text-dark-brown">Nom de l'entreprise</label>
                <input type="text" v-model="profileData.company_name" id="companyName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
            <div>
                <label for="siret" class="block text-sm font-medium text-dark-brown">SIRET</label>
                <input type="text" v-model="profileData.siret" id="siret" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
            <!-- ... other company fields: address, city, etc. -->
        </div>

        <div class="mt-8 flex justify-end">
            <button type="submit" class="bg-truffle-burgundy text-cream font-sans py-3 px-6 rounded-lg hover:bg-dark-brown transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gold">
                Enregistrer les modifications
            </button>
        </div>
      </form>

      <!-- User Management Section -->
      <div class="mt-10">
        <h3 class="text-xl font-serif text-dark-brown border-b border-gold pb-2 mb-4">Gestion des Utilisateurs</h3>
        <div class="bg-cream p-6 rounded-lg shadow">
          <div class="mb-6">
            <h4 class="font-medium text-lg text-dark-brown">Utilisateurs Actuels</h4>
            <ul class="mt-2 divide-y divide-gray-200">
              <li v-for="user in users" :key="user.id" class="flex justify-between items-center py-3">
                <div>
                  <p class="font-semibold text-dark-brown">{{ user.first_name }} {{ user.last_name }} ({{ user.email }})</p>
                  <span class="text-xs uppercase font-bold text-gray-500">{{ user.role }}</span>
                </div>
                <button 
                  v-if="currentUserIsAdmin && user.id !== authStore.user.id" 
                  @click="removeUser(user.id)"
                  class="text-red-600 hover:text-red-800 text-sm font-semibold transition-colors duration-200">
                  Supprimer
                </button>
              </li>
            </ul>
          </div>

          <div v-if="currentUserIsAdmin">
            <h4 class="font-medium text-lg text-dark-brown mb-3">Ajouter un Nouvel Utilisateur</h4>
            <form @submit.prevent="addUser">
               <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                 <input v-model="newUser.first_name" type="text" placeholder="Prénom" class="p-2 border border-gray-300 rounded-md" required>
                 <input v-model="newUser.last_name" type="text" placeholder="Nom" class="p-2 border border-gray-300 rounded-md" required>
                 <input v-model="newUser.email" type="email" placeholder="Adresse e-mail" class="p-2 border border-gray-300 rounded-md col-span-1 md:col-span-2" required>
                 <input v-model="newUser.password" type="password" placeholder="Mot de passe temporaire" class="p-2 border border-gray-300 rounded-md col-span-1 md:col-span-2" required>
              </div>
              <button type="submit" class="bg-truffle-burgundy text-cream font-sans py-2 px-5 rounded-lg hover:bg-dark-brown transition-colors duration-300">
                Ajouter l'utilisateur
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../../stores/auth'; // Assuming a B2B store is not needed if authStore holds all user info
import { useNotificationStore } from '../../stores/notification';
import apiClient from '../../api-client';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const profile = computed(() => authStore.user);
const isLoading = ref(true);
const users = ref([]);
const currentUserIsAdmin = computed(() => profile.value && profile.value.role === 'admin');

// Use a local ref for form data to avoid direct mutation of store state
const profileData = ref({});
const newUser = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  role: 'member', // Default role
});

async function fetchInitialData() {
  isLoading.value = true;
  try {
    // If user is not yet in store, check session
    if (!authStore.user) {
      await authStore.checkSession();
    }
    // Now that user is available, fetch related users
    if(authStore.isB2BAuthenticated) {
        const response = await apiClient.get('/api/b2b/users');
        users.value = response.data;
    }
  } catch (error) {
      notificationStore.showNotification('Could not load profile data.', 'error');
  } finally {
      isLoading.value = false;
  }
}

onMounted(fetchInitialData);

// When profile loads from store, populate the local form data
watch(profile, (newProfile) => {
  if (newProfile) {
    profileData.value = { 
        first_name: newProfile.first_name,
        last_name: newProfile.last_name,
        email: newProfile.email,
        company_name: newProfile.b2b_account?.company_name,
        siret: newProfile.b2b_account?.siret,
     };
  }
}, { immediate: true, deep: true });


const handleUpdateProfile = async () => {
    try {
        await apiClient.put('/api/b2b/profile', profileData.value);
        notificationStore.showNotification('Profile updated successfully!', 'success');
        // Refresh the auth store user data after update
        await authStore.checkSession();
    } catch (error) {
        notificationStore.showNotification(error.response?.data?.error || 'Failed to update profile.', 'error');
    }
};

const addUser = async () => {
  try {
    await apiClient.post('/api/b2b/users/add', newUser);
    notificationStore.showNotification('User added successfully!', 'success');
    // Reset form and refresh user list
    Object.keys(newUser).forEach(key => newUser[key] = '');
    await fetchInitialData(); 
  } catch (error) {
    notificationStore.showNotification(error.response?.data?.error || 'Failed to add user.', 'error');
  }
};

const removeUser = async (userId) => {
  if (window.confirm("Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.")) {
    try {
      await apiClient.post('/api/b2b/users/remove', { user_id: userId });
      notificationStore.showNotification('User removed successfully.', 'success');
      await fetchInitialData(); // Refresh the list
    } catch (error) {
      notificationStore.showNotification(error.response?.data?.error || 'Failed to remove user.', 'error');
    }
  }
};
</script>
