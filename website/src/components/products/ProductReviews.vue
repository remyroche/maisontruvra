<!-- website/src/components/products/ProductReviews.vue -->
<template>
  <div class="mt-16">
    <h2 class="text-2xl font-bold tracking-tight text-gray-900">Avis des Clients</h2>

    <!-- Review Submission Form -->
    <div v-if="userStore.isAuthenticated" class="mt-6">
      <h3 class="text-lg font-medium text-gray-900">Partagez votre expérience</h3>
      <form @submit.prevent="handleReviewSubmit" class="mt-4 space-y-4">
        <div>
          <label for="rating" class="block text-sm font-medium text-gray-700">Votre note</label>
          <div class="flex items-center mt-1">
            <StarIcon v-for="i in 5" :key="i"
              @click="newReview.rating = i"
              :class="[i <= newReview.rating ? 'text-yellow-400' : 'text-gray-300', 'h-6 w-6 cursor-pointer']"
              aria-hidden="true" />
          </div>
        </div>
        <div>
          <label for="comment" class="block text-sm font-medium text-gray-700">Votre avis</label>
          <textarea id="comment" v-model="newReview.comment" rows="4" required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
        </div>
        <div class="flex justify-end">
          <button type="submit" :disabled="isSubmitting"
            class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50">
            {{ isSubmitting ? 'Envoi en cours...' : 'Soumettre l\'avis' }}
          </button>
        </div>
      </form>
    </div>
    <div v-else class="mt-6 p-4 bg-gray-50 rounded-md">
        <p class="text-sm text-gray-600">Vous devez être <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">connecté</router-link> pour laisser un avis.</p>
    </div>

    <!-- Existing Reviews List -->
    <div class="mt-10 border-t border-gray-200 pt-10">
      <div v-if="isLoading" class="text-center text-gray-500">Chargement des avis...</div>
      <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
      <div v-else-if="reviews.length === 0" class="text-center text-gray-500">
        Il n'y a pas encore d'avis pour ce produit. Soyez le premier à en laisser un !
      </div>
      <div v-else class="space-y-10">
        <div v-for="review in reviews" :key="review.id" class="flex flex-col sm:flex-row">
          <div class="mt-4 sm:ml-6 sm:mt-0">
            <h4 class="text-sm font-bold text-gray-900">{{ review.user.name || 'Utilisateur Anonyme' }}</h4>
            <div class="mt-1 flex items-center">
              <StarIcon v-for="i in 5" :key="i" :class="[i <= review.rating ? 'text-yellow-400' : 'text-gray-300', 'h-5 w-5 flex-shrink-0']" aria-hidden="true" />
            </div>
            <p class="mt-2 text-sm text-gray-600">{{ new Date(review.created_at).toLocaleDateString() }}</p>
          </div>
          <div class="mt-4 sm:ml-auto sm:pl-4 sm:border-l sm:border-gray-200">
            <p class="text-base text-gray-600">{{ review.comment }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue';
import { StarIcon } from '@heroicons/vue/24/solid';
import { useUserStore } from '@/stores/user'; // Assuming a user store for auth status
import api from '@/services/api'; // Assuming a configured axios instance

const props = defineProps({
  productId: {
    type: [Number, String],
    required: true,
  },
});

const userStore = useUserStore();
const reviews = ref([]);
const newReview = ref({
  rating: 0,
  comment: '',
});
const isLoading = ref(true);
const isSubmitting = ref(false);
const error = ref(null);

const fetchReviews = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get(`/products/${props.productId}/reviews`);
    reviews.value = response.data;
  } catch (err) {
    console.error("Failed to fetch reviews:", err);
    error.value = "Impossible de charger les avis.";
  } finally {
    isLoading.value = false;
  }
};

const handleReviewSubmit = async () => {
  if (newReview.value.rating === 0) {
    alert("Veuillez sélectionner une note.");
    return;
  }
  isSubmitting.value = true;
  error.value = null;
  try {
    const response = await api.post(`/products/${props.productId}/reviews`, {
      rating: newReview.value.rating,
      comment: newReview.value.comment,
    });
    // Add the new review to the top of the list for immediate feedback
    reviews.value.unshift(response.data);
    // Reset form
    newReview.value.rating = 0;
    newReview.value.comment = '';
  } catch (err) {
    console.error("Failed to submit review:", err);
    error.value = err.response?.data?.error || "Une erreur est survenue lors de l'envoi de votre avis.";
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchReviews();
});
</script>
