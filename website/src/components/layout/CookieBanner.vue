<template>
  <div
    v-if="showBanner"
    class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-40"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
        <div class="flex-1">
          <p class="text-sm text-gray-700">
            Nous utilisons des cookies pour améliorer votre expérience sur notre site. 
            En continuant à naviguer, vous acceptez notre utilisation des cookies.
            <router-link 
              to="/politique-confidentialite" 
              class="text-brand-burgundy hover:underline ml-1"
            >
              En savoir plus
            </router-link>
          </p>
        </div>
        
        <div class="flex space-x-3">
          <button
            @click="acceptCookies"
            class="bg-brand-burgundy text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-opacity-90 transition-colors"
          >
            Accepter
          </button>
          <button
            @click="declineCookies"
            class="border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Refuser
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const showBanner = ref(false);

onMounted(() => {
  // Check if user has already made a choice
  const cookieConsent = localStorage.getItem('cookieConsent');
  if (!cookieConsent) {
    showBanner.value = true;
  }
});

function acceptCookies() {
  localStorage.setItem('cookieConsent', 'accepted');
  showBanner.value = false;
  
  // Enable analytics and other tracking cookies here
  // Example: gtag('consent', 'update', { analytics_storage: 'granted' });
}

function declineCookies() {
  localStorage.setItem('cookieConsent', 'declined');
  showBanner.value = false;
  
  // Disable analytics and other tracking cookies here
  // Example: gtag('consent', 'update', { analytics_storage: 'denied' });
}
</script>