<template>
  <div>
    <h2 class="text-3xl font-serif text-truffle-burgundy mb-6">My Professional Profile</h2>
    <div v-if="isLoading" class="text-center">Loading profile...</div>
    <form v-else-if="profile" @submit.prevent="handleUpdateProfile">
        <!-- User Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-cream rounded-lg shadow">
            <h3 class="col-span-full text-xl font-serif text-dark-brown border-b border-gold pb-2">User Information</h3>
            <div>
                <label for="firstName" class="block text-sm font-medium text-dark-brown">First Name</label>
                <input type="text" v-model="profileData.first_name" id="firstName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
            <div>
                <label for="lastName" class="block text-sm font-medium text-dark-brown">Last Name</label>
                <input type="text" v-model="profileData.last_name" id="lastName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
             <div>
                <label for="email" class="block text-sm font-medium text-dark-brown">Email</label>
                <input type="email" v-model="profileData.email" id="email" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-gold focus:border-gold">
            </div>
        </div>
        
        <!-- Company Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-cream rounded-lg shadow mt-8">
            <h3 class="col-span-full text-xl font-serif text-dark-brown border-b border-gold pb-2">Company Information</h3>
            <div>
                <label for="companyName" class="block text-sm font-medium text-dark-brown">Company Name</label>
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
                Save Changes
            </button>
        </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useB2BStore } from '../../stores/b2b';

const b2bStore = useB2BStore();
const profile = computed(() => b2bStore.profile);
const isLoading = computed(() => b2bStore.isLoading);

// Use a local ref for form data to avoid direct mutation of store state
const profileData = ref({});

onMounted(async () => {
  await b2bStore.fetchProfile();
});

// When profile loads from store, populate the local form data
watch(profile, (newProfile) => {
  if (newProfile) {
    profileData.value = { ...newProfile };
  }
}, { immediate: true });


const handleUpdateProfile = async () => {
    try {
        await b2bStore.updateProfile(profileData.value);
        alert('Profile updated successfully!'); // Replace with a proper UI notification
    } catch (error) {
        alert('Failed to update profile.'); // Replace with a proper UI notification
    }
};
</script>
