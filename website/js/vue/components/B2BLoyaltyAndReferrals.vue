<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-semibold text-gray-800 mb-4">Programme de Fidélité et Parrainage</h2>
    
    <!-- Loyalty Status -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-gray-800">Votre Statut de Fidélité</h3>
      <div v-if="b2bPortalStore.loyaltyData" class="mt-2">
        <p>Niveau Actuel : <span class="font-bold text-primary">{{ b2bPortalStore.loyaltyData.current_tier.name }}</span></p>
        <p>Points : <span class="font-bold">{{ b2bPortalStore.loyaltyData.points }}</span></p>
        <div v-if="b2bPortalStore.loyaltyData.next_tier">
          <p>Prochain niveau : {{ b2bPortalStore.loyaltyData.next_tier.name }} (à {{ b2bPortalStore.loyaltyData.next_tier.points_required }} points)</p>
          <div class="w-full bg-gray-200 rounded-full h-2.5 mt-2">
            <div class="bg-primary h-2.5 rounded-full" :style="{ width: b2bPortalStore.loyaltyData.progress_to_next_tier + '%' }"></div>
          </div>
        </div>
        <p class="mt-2 text-sm text-gray-600">Avantages : {{ b2bPortalStore.loyaltyData.current_tier.benefits }}</p>
      </div>
       <div v-else class="mt-2 text-gray-500">
        Chargement des données de fidélité...
      </div>
    </div>

    <!-- Referral Program -->
    <div>
      <h3 class="text-xl font-semibold text-gray-800">Programme de Parrainage</h3>
      <div v-if="b2bPortalStore.referralCode" class="mt-2">
        <p class="text-gray-600">Invitez d'autres professionnels à rejoindre Maison Truvra et recevez des récompenses pour chaque nouveau client qui passe une commande.</p>
        
        <div class="mt-4 p-4 bg-gray-50 rounded-lg border">
          <p class="text-lg">Votre code de parrainage unique : <span class="font-bold text-primary">{{ b2bPortalStore.referralCode }}</span></p>
          <div class="mt-4 flex flex-wrap items-center gap-2">
            <button @click="copyReferralCode" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 flex items-center text-sm">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
              Copier le code
            </button>
            <button @click="copyReferralLink" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 flex items-center text-sm">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
              Copier le lien
            </button>
          </div>
        </div>

        <div class="mt-6">
          <p class="text-gray-600">Ou partagez directement par :</p>
          <div class="mt-2 flex items-center space-x-2">
            <button @click="shareByEmail" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path></svg>
              Email
            </button>
            <button @click="shareByWhatsapp" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.894 11.892-1.99 0-3.903-.52-5.586-1.456l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 4.315 1.731 6.086l.107.175-.32 1.181 1.221-.314.174.104z"/></svg>
              WhatsApp
            </button>
          </div>
        </div>
      </div>
      <div v-else class="mt-2 text-gray-500">
        Chargement des données de parrainage...
      </div>

      <div class="mt-6">
        <h4 class="text-lg font-semibold text-gray-700">Vos filleuls</h4>
        <div v-if="b2bPortalStore.referrals && b2bPortalStore.referrals.length > 0" class="mt-2">
          <ul class="divide-y divide-gray-200">
            <li v-for="referral in b2bPortalStore.referrals" :key="referral.id" class="py-3 flex justify-between items-center">
              <span>{{ referral.referred_user_email }}</span>
              <span :class="['px-2 inline-flex text-xs leading-5 font-semibold rounded-full', referral.status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800']">
                {{ referral.status === 'Completed' ? 'Complété' : 'En attente' }}
              </span>
            </li>
          </ul>
        </div>
        <p v-else class="mt-2 text-gray-500">Vous n'avez pas encore de filleuls.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useB2BPortalStore } from '../../stores/b2b-portal';
import { useNotificationStore } from '../../stores/notification';

// Component state and actions using Pinia stores
const b2bPortalStore = useB2BPortalStore();
const notificationStore = useNotificationStore();

/**
 * Fetches loyalty and referral data when the component is mounted.
 */
onMounted(() => {
  b2bPortalStore.getB2BLoyaltyData();
  b2bPortalStore.getB2BReferralData();
});

/**
 * A computed property to generate the full referral link.
 * @returns {string} The complete referral URL.
 */
const referralLink = computed(() => {
  if (b2bPortalStore.referralCode) {
    // Constructs the referral link using the current window origin and the user's referral code.
    return `${window.location.origin}/pro/register?ref=${b2bPortalStore.referralCode}`;
  }
  return '';
});

/**
 * Copies the provided text to the clipboard and shows a notification.
 * @param {string} text - The text to copy.
 * @param {string} successMessage - The message to show on successful copy.
 */
function copyToClipboard(text, successMessage) {
    // Uses the modern Clipboard API if available.
    if (!navigator.clipboard) {
        // Fallback for older browsers.
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed"; // Prevents scrolling to the bottom of the page.
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            notificationStore.showNotification({ message: successMessage, type: 'success' });
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            notificationStore.showNotification({ message: "Erreur lors de la copie.", type: 'error' });
        }
        document.body.removeChild(textArea);
        return;
    }
    // Uses the Clipboard API to write text.
    navigator.clipboard.writeText(text).then(() => {
        notificationStore.showNotification({ message: successMessage, type: 'success' });
    }, (err) => {
        console.error('Could not copy text: ', err);
        notificationStore.showNotification({ message: "Erreur lors de la copie.", type: 'error' });
    });
}

/**
 * Copies the user's referral code to the clipboard.
 */
const copyReferralCode = () => {
  if (b2bPortalStore.referralCode) {
    copyToClipboard(b2bPortalStore.referralCode, 'Code de parrainage copié !');
  }
};

/**
 * Copies the user's referral link to the clipboard.
 */
const copyReferralLink = () => {
  if (referralLink.value) {
    copyToClipboard(referralLink.value, 'Lien de parrainage copié !');
  }
};

/**
 * Opens the user's default email client with a pre-filled referral message.
 */
const shareByEmail = () => {
  if (!referralLink.value) return;
  const subject = "Invitation à rejoindre Maison Truvra Pro";
  const body = `Bonjour,\n\nJe vous invite à découvrir Maison Truvra, notre fournisseur d'ingrédients de qualité pour les professionnels.\n\nInscrivez-vous via mon lien de parrainage pour bénéficier d'avantages : ${referralLink.value}\n\nCordialement,`;
  const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  window.open(mailtoLink, '_blank');
};

/**
 * Opens WhatsApp with a pre-filled referral message.
 */
const shareByWhatsapp = () => {
  if (!referralLink.value) return;
  const text = `Bonjour, je vous invite à découvrir Maison Truvra, notre fournisseur d'ingrédients de qualité pour les professionnels. Inscrivez-vous via mon lien de parrainage pour bénéficier d'avantages : ${referralLink.value}`;
  // wa.me is the recommended universal link for WhatsApp.
  const whatsappLink = `https://wa.me/?text=${encodeURIComponent(text)}`;
  window.open(whatsappLink, '_blank');
};
</script>
