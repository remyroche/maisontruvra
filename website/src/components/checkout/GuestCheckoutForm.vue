<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Informations de contact</h3>
    
    <form @submit.prevent="submitGuestInfo" class="space-y-4">
      <!-- Email -->
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
          Adresse email *
        </label>
        <input 
          id="email"
          v-model="form.email"
          type="email" 
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.email }"
          placeholder="votre@email.com"
          @blur="validateEmail"
        >
        <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
        <p class="mt-1 text-sm text-gray-500">
          Nous utiliserons cette adresse pour vous envoyer la confirmation de commande et les informations de suivi.
        </p>
      </div>

      <!-- Phone -->
      <div>
        <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
          Téléphone *
        </label>
        <input 
          id="phone"
          v-model="form.phone"
          type="tel" 
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.phone }"
          placeholder="06 12 34 56 78"
          @blur="validatePhone"
        >
        <p v-if="errors.phone" class="mt-1 text-sm text-red-600">{{ errors.phone }}</p>
        <p class="mt-1 text-sm text-gray-500">
          Nécessaire pour la livraison et en cas de problème avec votre commande.
        </p>
      </div>

      <!-- First Name -->
      <div>
        <label for="firstName" class="block text-sm font-medium text-gray-700 mb-1">
          Prénom *
        </label>
        <input 
          id="firstName"
          v-model="form.firstName"
          type="text" 
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.firstName }"
          @blur="validateFirstName"
        >
        <p v-if="errors.firstName" class="mt-1 text-sm text-red-600">{{ errors.firstName }}</p>
      </div>

      <!-- Last Name -->
      <div>
        <label for="lastName" class="block text-sm font-medium text-gray-700 mb-1">
          Nom *
        </label>
        <input 
          id="lastName"
          v-model="form.lastName"
          type="text" 
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
          :class="{ 'border-red-500': errors.lastName }"
          @blur="validateLastName"
        >
        <p v-if="errors.lastName" class="mt-1 text-sm text-red-600">{{ errors.lastName }}</p>
      </div>

      <!-- Newsletter Subscription -->
      <div class="flex items-start">
        <input 
          id="newsletter"
          v-model="form.subscribeNewsletter"
          type="checkbox" 
          class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
        >
        <label for="newsletter" class="ml-2 text-sm text-gray-700">
          Je souhaite recevoir les actualités et offres spéciales de Maison Truvra par email
        </label>
      </div>

      <!-- Marketing Consent -->
      <div class="flex items-start">
        <input 
          id="marketing"
          v-model="form.marketingConsent"
          type="checkbox" 
          class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
        >
        <label for="marketing" class="ml-2 text-sm text-gray-700">
          J'accepte de recevoir des communications marketing personnalisées
        </label>
      </div>

      <!-- Terms and Conditions -->
      <div class="flex items-start">
        <input 
          id="terms"
          v-model="form.acceptTerms"
          type="checkbox" 
          required
          class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
          :class="{ 'border-red-500': errors.acceptTerms }"
        >
        <label for="terms" class="ml-2 text-sm text-gray-700">
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
      <p v-if="errors.acceptTerms" class="text-sm text-red-600">{{ errors.acceptTerms }}</p>

      <!-- Account Creation Option -->
      <div class="bg-blue-50 p-4 rounded-lg">
        <div class="flex items-start">
          <input 
            id="createAccount"
            v-model="form.createAccount"
            type="checkbox" 
            class="mt-1 text-brand-burgundy focus:ring-brand-burgundy"
          >
          <div class="ml-2">
            <label for="createAccount" class="text-sm font-medium text-blue-900">
              Créer un compte pour faciliter mes prochains achats
            </label>
            <p class="text-sm text-blue-700 mt-1">
              Vous pourrez suivre vos commandes, gérer vos adresses et accéder à votre programme de fidélité.
            </p>
          </div>
        </div>

        <!-- Password fields (shown only if creating account) -->
        <div v-if="form.createAccount" class="mt-4 space-y-3">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe *
            </label>
            <input 
              id="password"
              v-model="form.password"
              type="password" 
              :required="form.createAccount"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              :class="{ 'border-red-500': errors.password }"
              @blur="validatePassword"
            >
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
              Confirmer le mot de passe *
            </label>
            <input 
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password" 
              :required="form.createAccount"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-brand-burgundy focus:border-brand-burgundy"
              :class="{ 'border-red-500': errors.confirmPassword }"
              @blur="validateConfirmPassword"
            >
            <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</p>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="pt-4">
        <button 
          type="submit" 
          :disabled="!isFormValid || isSubmitting"
          class="w-full bg-brand-burgundy text-white py-3 px-4 rounded-md font-medium hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Validation...' : 'Continuer vers la livraison' }}
        </button>
      </div>

      <!-- Login Link -->
      <div class="text-center pt-4 border-t">
        <p class="text-sm text-gray-600">
          Vous avez déjà un compte ?
          <button 
            type="button"
            @click="$emit('switch-to-login')"
            class="text-brand-burgundy hover:underline font-medium"
          >
            Se connecter
          </button>
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const emit = defineEmits(['guest-info-submitted', 'switch-to-login']);

// Form data
const form = ref({
  email: '',
  phone: '',
  firstName: '',
  lastName: '',
  subscribeNewsletter: false,
  marketingConsent: false,
  acceptTerms: false,
  createAccount: false,
  password: '',
  confirmPassword: ''
});

// Form validation
const errors = ref({});
const isSubmitting = ref(false);

// Computed
const isFormValid = computed(() => {
  return form.value.email && 
         form.value.phone && 
         form.value.firstName && 
         form.value.lastName && 
         form.value.acceptTerms &&
         Object.keys(errors.value).length === 0 &&
         (!form.value.createAccount || (form.value.password && form.value.confirmPassword));
});

// Validation methods
function validateEmail() {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!form.value.email) {
    errors.value.email = 'L\'adresse email est requise';
  } else if (!emailRegex.test(form.value.email)) {
    errors.value.email = 'Veuillez saisir une adresse email valide';
  } else {
    delete errors.value.email;
  }
}

function validatePhone() {
  const phoneRegex = /^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$/;
  if (!form.value.phone) {
    errors.value.phone = 'Le numéro de téléphone est requis';
  } else if (!phoneRegex.test(form.value.phone.replace(/\s/g, ''))) {
    errors.value.phone = 'Veuillez saisir un numéro de téléphone français valide';
  } else {
    delete errors.value.phone;
  }
}

function validateFirstName() {
  if (!form.value.firstName.trim()) {
    errors.value.firstName = 'Le prénom est requis';
  } else if (form.value.firstName.trim().length < 2) {
    errors.value.firstName = 'Le prénom doit contenir au moins 2 caractères';
  } else {
    delete errors.value.firstName;
  }
}

function validateLastName() {
  if (!form.value.lastName.trim()) {
    errors.value.lastName = 'Le nom est requis';
  } else if (form.value.lastName.trim().length < 2) {
    errors.value.lastName = 'Le nom doit contenir au moins 2 caractères';
  } else {
    delete errors.value.lastName;
  }
}

function validatePassword() {
  if (form.value.createAccount) {
    if (!form.value.password) {
      errors.value.password = 'Le mot de passe est requis';
    } else if (form.value.password.length < 8) {
      errors.value.password = 'Le mot de passe doit contenir au moins 8 caractères';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(form.value.password)) {
      errors.value.password = 'Le mot de passe doit contenir au moins une minuscule, une majuscule et un chiffre';
    } else {
      delete errors.value.password;
    }
  } else {
    delete errors.value.password;
  }
}

function validateConfirmPassword() {
  if (form.value.createAccount) {
    if (!form.value.confirmPassword) {
      errors.value.confirmPassword = 'La confirmation du mot de passe est requise';
    } else if (form.value.password !== form.value.confirmPassword) {
      errors.value.confirmPassword = 'Les mots de passe ne correspondent pas';
    } else {
      delete errors.value.confirmPassword;
    }
  } else {
    delete errors.value.confirmPassword;
  }
}

function validateTerms() {
  if (!form.value.acceptTerms) {
    errors.value.acceptTerms = 'Vous devez accepter les conditions générales';
  } else {
    delete errors.value.acceptTerms;
  }
}

// Submit handler
async function submitGuestInfo() {
  // Validate all fields
  validateEmail();
  validatePhone();
  validateFirstName();
  validateLastName();
  validateTerms();
  
  if (form.value.createAccount) {
    validatePassword();
    validateConfirmPassword();
  }

  if (!isFormValid.value) {
    return;
  }

  isSubmitting.value = true;
  
  try {
    // Prepare the data to emit
    const guestData = {
      email: form.value.email.trim(),
      phone: form.value.phone.trim(),
      firstName: form.value.firstName.trim(),
      lastName: form.value.lastName.trim(),
      subscribeNewsletter: form.value.subscribeNewsletter,
      marketingConsent: form.value.marketingConsent,
      createAccount: form.value.createAccount
    };

    if (form.value.createAccount) {
      guestData.password = form.value.password;
    }

    emit('guest-info-submitted', guestData);
  } catch (error) {
    console.error('Error submitting guest info:', error);
  } finally {
    isSubmitting.value = false;
  }
}

// Expose form data for parent component
defineExpose({
  form: computed(() => form.value),
  isValid: isFormValid,
  validate: () => {
    validateEmail();
    validatePhone();
    validateFirstName();
    validateLastName();
    validateTerms();
    if (form.value.createAccount) {
      validatePassword();
      validateConfirmPassword();
    }
    return isFormValid.value;
  }
});
</script>