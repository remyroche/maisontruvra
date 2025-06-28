<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Informations de paiement</h3>
    
    <!-- Payment Method Selection -->
    <div class="space-y-4 mb-6">
      <h4 class="font-medium text-gray-900">Mode de paiement</h4>
      
      <!-- Credit Card -->
      <div class="border rounded-lg p-4" :class="{ 'border-brand-burgundy bg-brand-cream': paymentMethod === 'card' }">
        <div class="flex items-center mb-3">
          <input 
            id="card"
            v-model="paymentMethod"
            type="radio" 
            value="card"
            class="text-brand-burgundy focus:ring-brand-burgundy"
          >
          <label for="card" class="ml-2 font-medium">Carte bancaire</label>
          <div class="ml-auto flex space-x-2">
            <img src="/images/visa.svg" alt="Visa" class="h-6" onerror="this.style.display='none'">
            <img src="/images/mastercard.svg" alt="Mastercard" class="h-6" onerror="this.style.display='none'">
          </div>
        </div>
        <p class="text-sm text-gray-600">Paiement sécurisé par Stripe</p>
      </div>

      <!-- PayPal (disabled for now) -->
      <div class="border rounded-lg p-4 opacity-50">
        <div class="flex items-center">
          <input 
            id="paypal"
            type="radio" 
            value="paypal"
            disabled
            class="text-brand-burgundy focus:ring-brand-burgundy"
          >
          <label for="paypal" class="ml-2 font-medium text-gray-500">PayPal</label>
          <span class="ml-auto text-sm text-gray-500">Bientôt disponible</span>
        </div>
      </div>
    </div>

    <!-- Credit Card Form -->
    <div v-if="paymentMethod === 'card'" class="space-y-4">
      <div>
        <label for="cardNumber" class="block text-sm font-medium text-gray-700 mb-1">
          Numéro de carte *
        </label>
        <input 
          id="cardNumber"
          v-model="cardForm.number"
          type="text" 
          required
          placeholder="1234 5678 9012 3456"
          maxlength="19"
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.number }"
          @input="formatCardNumber"
          @blur="validateCardNumber"
        >
        <p v-if="errors.number" class="mt-1 text-sm text-red-600">{{ errors.number }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="cardExpiry" class="block text-sm font-medium text-gray-700 mb-1">
            Date d'expiration *
          </label>
          <input 
            id="cardExpiry"
            v-model="cardForm.expiry"
            type="text" 
            required
            placeholder="MM/AA"
            maxlength="5"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            :class="{ 'border-red-500': errors.expiry }"
            @input="formatExpiry"
            @blur="validateExpiry"
          >
          <p v-if="errors.expiry" class="mt-1 text-sm text-red-600">{{ errors.expiry }}</p>
        </div>

        <div>
          <label for="cardCvc" class="block text-sm font-medium text-gray-700 mb-1">
            Code CVC *
          </label>
          <input 
            id="cardCvc"
            v-model="cardForm.cvc"
            type="text" 
            required
            placeholder="123"
            maxlength="4"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
            :class="{ 'border-red-500': errors.cvc }"
            @blur="validateCvc"
          >
          <p v-if="errors.cvc" class="mt-1 text-sm text-red-600">{{ errors.cvc }}</p>
        </div>
      </div>

      <div>
        <label for="cardName" class="block text-sm font-medium text-gray-700 mb-1">
          Nom sur la carte *
        </label>
        <input 
          id="cardName"
          v-model="cardForm.name"
          type="text" 
          required
          placeholder="Jean Dupont"
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.name }"
          @blur="validateName"
        >
        <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
      </div>

      <!-- Save Card Option -->
      <div v-if="!isGuestMode" class="flex items-center">
        <input 
          id="saveCard"
          v-model="cardForm.saveCard"
          type="checkbox" 
          class="text-brand-burgundy focus:ring-brand-burgundy"
        >
        <label for="saveCard" class="ml-2 text-sm text-gray-700">
          Enregistrer cette carte pour mes prochains achats
        </label>
      </div>
    </div>

    <!-- Security Notice -->
    <div class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-green-600 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <div class="text-sm">
          <p class="font-medium text-green-800">Paiement 100% sécurisé</p>
          <p class="text-green-700 mt-1">
            Vos informations de paiement sont chiffrées et sécurisées par Stripe. 
            Nous ne stockons jamais vos données bancaires.
          </p>
        </div>
      </div>
    </div>

    <!-- Terms and Conditions -->
    <div class="mt-6 flex items-start">
      <input 
        id="acceptTerms"
        v-model="acceptTerms"
        type="checkbox" 
        required
        class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
        :class="{ 'border-red-500': errors.acceptTerms }"
      >
      <label for="acceptTerms" class="ml-2 text-sm text-gray-700">
        J'accepte les 
        <router-link to="/conditions-generales" class="text-brand-burgundy hover:underline" target="_blank">
          conditions générales de vente
        </router-link>
        et la 
        <router-link to="/politique-confidentialite" class="text-brand-burgundy hover:underline" target="_blank">
          politique de confidentialité
        </router-link>
        *
      </label>
    </div>
    <p v-if="errors.acceptTerms" class="mt-1 text-sm text-red-600">{{ errors.acceptTerms }}</p>

    <!-- Error Message -->
    <div v-if="paymentError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
      <div class="flex">
        <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="ml-2 text-sm text-red-600">{{ paymentError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isGuestMode: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['payment-validated']);

// State
const paymentMethod = ref('card');
const acceptTerms = ref(false);
const paymentError = ref('');

const cardForm = ref({
  number: '',
  expiry: '',
  cvc: '',
  name: '',
  saveCard: false
});

const errors = ref({});

// Computed
const isFormValid = computed(() => {
  return paymentMethod.value === 'card' &&
         cardForm.value.number &&
         cardForm.value.expiry &&
         cardForm.value.cvc &&
         cardForm.value.name &&
         acceptTerms.value &&
         Object.keys(errors.value).length === 0;
});

// Validation methods
function validateCardNumber() {
  const number = cardForm.value.number.replace(/\s/g, '');
  if (!number) {
    errors.value.number = 'Le numéro de carte est requis';
  } else if (number.length < 13 || number.length > 19) {
    errors.value.number = 'Numéro de carte invalide';
  } else if (!luhnCheck(number)) {
    errors.value.number = 'Numéro de carte invalide';
  } else {
    delete errors.value.number;
  }
}

function validateExpiry() {
  const expiry = cardForm.value.expiry;
  if (!expiry) {
    errors.value.expiry = 'La date d\'expiration est requise';
  } else if (!/^\d{2}\/\d{2}$/.test(expiry)) {
    errors.value.expiry = 'Format invalide (MM/AA)';
  } else {
    const [month, year] = expiry.split('/');
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear() % 100;
    const currentMonth = currentDate.getMonth() + 1;
    
    if (parseInt(month) < 1 || parseInt(month) > 12) {
      errors.value.expiry = 'Mois invalide';
    } else if (parseInt(year) < currentYear || (parseInt(year) === currentYear && parseInt(month) < currentMonth)) {
      errors.value.expiry = 'Carte expirée';
    } else {
      delete errors.value.expiry;
    }
  }
}

function validateCvc() {
  const cvc = cardForm.value.cvc;
  if (!cvc) {
    errors.value.cvc = 'Le code CVC est requis';
  } else if (!/^\d{3,4}$/.test(cvc)) {
    errors.value.cvc = 'Code CVC invalide';
  } else {
    delete errors.value.cvc;
  }
}

function validateName() {
  const name = cardForm.value.name.trim();
  if (!name) {
    errors.value.name = 'Le nom sur la carte est requis';
  } else if (name.length < 2) {
    errors.value.name = 'Le nom doit contenir au moins 2 caractères';
  } else {
    delete errors.value.name;
  }
}

// Formatting methods
function formatCardNumber(event) {
  let value = event.target.value.replace(/\s/g, '');
  value = value.replace(/\D/g, '');
  value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
  cardForm.value.number = value;
}

function formatExpiry(event) {
  let value = event.target.value.replace(/\D/g, '');
  if (value.length >= 2) {
    value = value.substring(0, 2) + '/' + value.substring(2, 4);
  }
  cardForm.value.expiry = value;
}

// Luhn algorithm for card validation
function luhnCheck(cardNumber) {
  let sum = 0;
  let isEven = false;
  
  for (let i = cardNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cardNumber.charAt(i));
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
}

// Validation method for parent component
function validateForm() {
  validateCardNumber();
  validateExpiry();
  validateCvc();
  validateName();
  
  if (!acceptTerms.value) {
    errors.value.acceptTerms = 'Vous devez accepter les conditions générales';
  } else {
    delete errors.value.acceptTerms;
  }
  
  if (isFormValid.value) {
    emit('payment-validated', {
      method: paymentMethod.value,
      card: {
        number: cardForm.value.number.replace(/\s/g, ''),
        expiry: cardForm.value.expiry,
        cvc: cardForm.value.cvc,
        name: cardForm.value.name,
        saveCard: cardForm.value.saveCard
      }
    });
  }
  
  return isFormValid.value;
}

// Expose methods for parent component
defineExpose({
  validateForm,
  isValid: isFormValid,
  paymentData: computed(() => ({
    method: paymentMethod.value,
    card: cardForm.value,
    acceptTerms: acceptTerms.value
  }))
});
</script>