<template>
    <div class="max-w-4xl mx-auto">
        <!-- Login View -->
        <div v-if="currentView === 'login'">
            <div class="max-w-md mx-auto">
                <h1 class="text-3xl font-serif text-center mb-2">Espace Professionnel</h1>
                <p class="text-center text-gray-600 mb-8">Accédez à vos avantages exclusifs.</p>
                <div class="bg-white p-8 rounded-lg shadow-md">
                    <form @submit.prevent="handleLogin">
                        <div class="mb-4">
                            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                            <input type="email" v-model="loginForm.email" class="w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm" required>
                        </div>
                        <div class="mb-6">
                            <label for="password" class="block text-sm font-medium text-gray-700">Mot de passe</label>
                            <input type="password" v-model="loginForm.password" class="w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm" required>
                        </div>
                        <button type="submit" :disabled="loading" class="btn-primary w-full rounded-md py-2 disabled:opacity-50">
                            <span v-if="!loading">Se Connecter</span>
                            <span v-else>Connexion...</span>
                        </button>
                    </form>
                    <div class="text-center text-sm mt-6">
                        <a @click.prevent="currentView = 'forgotPassword'" href="#" class="font-medium text-indigo-600 hover:text-indigo-500">Mot de passe oublié ?</a>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow-md mt-6">
                    <button @click="showRegister = !showRegister" class="w-full flex justify-between items-center text-left px-8 py-4 font-semibold text-gray-800 focus:outline-none">
                        <span>Pas encore de compte ? Créez-en un</span>
                        <svg class="h-5 w-5 transform transition-transform" :class="{'rotate-180': showRegister}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </button>
                    <div v-if="showRegister" class="px-8 pb-6">
                        <p class="text-gray-600 mb-4 text-sm">Remplissez le formulaire ci-dessous. Notre équipe examinera votre demande et vous recevrez un email de confirmation une fois votre compte validé.</p>
                        <form @submit.prevent="handleRegister">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <input v-model="registerForm.companyName" type="text" placeholder="Nom de l'entreprise" class="p-2 border rounded-md" required>
                                <input v-model="registerForm.siret" type="text" placeholder="N° de SIRET" class="p-2 border rounded-md" required>
                                <input v-model="registerForm.contactName" type="text" placeholder="Nom du contact" class="p-2 border rounded-md" required>
                                <input v-model="registerForm.email" type="email" placeholder="Adresse e-mail" class="p-2 border rounded-md" required>
                                <input v-model="registerForm.password" type="password" placeholder="Mot de passe" class="p-2 border rounded-md" required>
                            </div>
                            <button type="submit" :disabled="loading" class="btn-primary w-full rounded-md py-2 mt-4 disabled:opacity-50">
                                <span v-if="!loading">Soumettre la demande</span>
                                <span v-else>Envoi...</span>
                            </button>
                        </form>
                    </div>
                </div>
                 <p class="text-center text-sm text-gray-600 mt-6">
                    Besoin d'aide ? Consultez notre <a @click.prevent="currentView = 'faq'" href="#" class="font-medium text-indigo-600 hover:text-indigo-500">FAQ pour les professionnels</a>.
                </p>
            </div>
        </div>

        <!-- Forgot Password View -->
        <div v-if="currentView === 'forgotPassword'">
            <div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
                <h1 class="text-3xl font-serif text-center mb-6">Réinitialiser le mot de passe</h1>
                <p class="text-center text-sm text-gray-600 mb-6">Entrez votre adresse e-mail et nous vous enverrons un lien pour réinitialiser votre mot de passe.</p>
                <form @submit.prevent="handleForgotPassword">
                    <div class="mb-4">
                        <label for="email-forgot" class="block text-sm font-medium text-gray-700">Email</label>
                        <input type="email" id="email-forgot" v-model="forgotPasswordForm.email" class="w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm" required>
                    </div>
                    <button type="submit" :disabled="loading" class="btn-primary w-full rounded-md py-2 disabled:opacity-50">
                         <span v-if="!loading">Envoyer le lien</span>
                         <span v-else>Envoi...</span>
                    </button>
                </form>
                <p class="text-center text-sm mt-6">
                    <a @click.prevent="currentView = 'login'" href="#" class="font-medium text-indigo-600 hover:text-indigo-500">Retour à la connexion</a>
                </p>
            </div>
        </div>
        
        <!-- FAQ View -->
        <div v-if="currentView === 'faq'">
            <h1 class="text-4xl font-serif text-center mb-4">Foire Aux Questions</h1>
            <p class="text-center text-gray-600 mb-12">Vous trouverez ici les réponses aux questions les plus fréquentes.</p>
            <div class="space-y-4 max-w-2xl mx-auto">
                <div v-for="(item, index) in faqItems" :key="index" class="accordion-item bg-white rounded-lg shadow-sm">
                    <button @click="toggleFaq(index)" class="accordion-header w-full flex justify-between items-center text-left px-6 py-4 font-semibold text-gray-800 focus:outline-none">
                        <span>{{ item.question }}</span>
                        <svg class="h-5 w-5 transform transition-transform" :class="{'rotate-180': openFaqIndex === index}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </button>
                    <div v-if="openFaqIndex === index" class="px-6 pb-4 text-gray-600">
                        <p>{{ item.answer }}</p>
                    </div>
                </div>
            </div>
             <p class="text-center text-sm mt-8">
                <a @click.prevent="currentView = 'login'" href="#" class="font-medium text-indigo-600 hover:text-indigo-500">Retour à la page de connexion</a>
            </p>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../js/stores/auth';
import { useNotificationStore } from '../../js/stores/notification';
import apiClient from '../../js/api-client';

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const currentView = ref('login'); // 'login', 'forgotPassword', 'faq'
const showRegister = ref(false);
const openFaqIndex = ref(null);
const loading = ref(false);

const loginForm = reactive({ email: '', password: '' });
const registerForm = reactive({ companyName: '', siret: '', contactName: '', email: '', password: '' });
const forgotPasswordForm = reactive({ email: '' });

const faqItems = ref([
    { question: "Comment créer un compte professionnel ?", answer: "Cliquez sur \"Créez-en un\" sur la page de connexion et remplissez le formulaire. Vous devrez fournir les informations de votre société, y compris votre numéro SIRET." },
    { question: "Quels sont les délais d'approbation pour un compte pro ?", answer: "Notre équipe examine les demandes dans les plus brefs délais. Vous recevrez un email de confirmation une fois votre compte validé et activé." },
    { question: "Y a-t-il un minimum de commande ?", answer: "Oui, un montant minimum de commande de 250€ HT est requis pour les comptes professionnels afin de bénéficier des tarifs préférentiels." },
    { question: "Qu’est-ce que le passeport produit ?", answer: "Chacun de nos produits est tracé. Il est enregistré sur une blockchain en interne au moment de la récolte, et les informations (date de traitement, etc.) le sont au moment du packaging. Chaque produit dispose d’un QR code unique qui renvoie vers son passeport." }
]);

function toggleFaq(index) {
    openFaqIndex.value = openFaqIndex.value === index ? null : index;
}

async function handleLogin() {
    loading.value = true;
    try {
        await authStore.loginB2B(loginForm);
        router.push('/pro/dashboard');
        notificationStore.showNotification('Connexion réussie !', 'success');
    } catch (error) {
        notificationStore.showNotification(error.data?.error || 'Email ou mot de passe incorrect.', 'error');
    } finally {
        loading.value = false;
    }
}

async function handleRegister() {
    loading.value = true;
    try {
        await apiClient.b2bRegister(registerForm);
        notificationStore.showNotification('Votre demande d\'inscription a été envoyée. Vous recevrez une confirmation par e-mail.', 'success');
        showRegister.value = false;
        // Reset form
        Object.keys(registerForm).forEach(key => registerForm[key] = '');
    } catch (error) {
        notificationStore.showNotification(error.data?.error || 'Une erreur est survenue lors de l\'inscription.', 'error');
    } finally {
        loading.value = false;
    }
}

async function handleForgotPassword() {
    loading.value = true;
    try {
        const response = await apiClient.b2bRequestPasswordReset(forgotPasswordForm.email);
        notificationStore.showNotification(response.message, 'success');
        currentView.value = 'login';
    } catch (error) {
        notificationStore.showNotification('Une erreur est survenue.', 'error');
    } finally {
        loading.value = false;
    }
}
</script>
