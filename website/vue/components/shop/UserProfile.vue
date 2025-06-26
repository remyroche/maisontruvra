<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Mon Compte</h2>
    
    <div v-if="userStore.user" class="mt-8">
      <h3 class="text-xl font-semibold">Sécurité</h3>
      <div class="mt-4 p-4 border rounded-lg">
        <h4 class="font-medium">Authentification à deux facteurs (A2F)</h4>

        <!-- State: 2FA is Disabled -->
        <div v-if="!userStore.user.two_factor_enabled">
          <p class="text-gray-600 my-2">Ajoutez une couche de sécurité supplémentaire à votre compte.</p>
          <button @click="handleEnableMFA" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Activer l'A2F
          </button>
          
          <!-- MFA Setup View -->
          <div v-if="userStore.mfaSetupData.secret" class="mt-4 p-4 bg-gray-50 rounded-md">
            <p class="font-semibold">1. Scannez ce code QR avec votre application d'authentification :</p>
            <img :src="userStore.mfaSetupData.qrCode" alt="QR Code A2F" class="my-2 border rounded" />
            <p class="mt-2 text-sm">Ou entrez cette clé manuellement :</p>
            <p class="font-mono bg-gray-200 p-2 rounded my-1 text-sm break-all">{{ userStore.mfaSetupData.secret }}</p>
            
            <p class="font-semibold mt-4">2. Entrez le code de vérification pour confirmer :</p>
            <div class="mt-2">
              <label for="totp-confirm" class="sr-only">Code de vérification</label>
              <input type="text" v-model="totpCode" id="totp-confirm" placeholder="123456" class="mt-1 w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              <div class="mt-2">
                <button @click="handleConfirmMFA" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                  Confirmer et Activer
                </button>
                 <button @click="cancelMfaSetup" class="ml-2 text-sm text-gray-600 hover:underline">
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- State: 2FA is Enabled -->
        <div v-else>
          <p class="text-green-700 bg-green-100 p-3 rounded-md my-2">L'authentification à deux facteurs est activée.</p>
          <button @click="handleDisableMFA" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
            Désactiver l'A2F
          </button>
        </div>
      </div>
    </div>
    <div v-else>
        <p>Chargement des informations utilisateur...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const totpCode = ref('');

onMounted(() => {
  // Fetch user data when component is mounted to get 2FA status
  if (!userStore.user) {
    userStore.fetchUser();
  }
});

async function handleEnableMFA() {
  await userStore.enableMFA();
}

async function handleConfirmMFA() {
  if (!totpCode.value) {
    alert('Veuillez entrer le code de vérification.');
    return;
  }
  const result = await userStore.confirmMFA(totpCode.value);
  if (result.success) {
    totpCode.value = '';
    alert('A2F activée avec succès !');
  } else {
    alert(`Erreur: ${result.error}`);
  }
}

async function handleDisableMFA() {
    if (confirm("Êtes-vous sûr de vouloir désactiver l'authentification à deux facteurs ?")) {
        const result = await userStore.disableMFA();
        if (result.success) {
            alert('A2F désactivée avec succès.');
        } else {
            alert(`Erreur: ${result.error}`);
        }
    }
}

function cancelMfaSetup() {
  userStore.clearMfaSetup();
}
</script>
