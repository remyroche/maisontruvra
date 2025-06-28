<template>
  <div class="reviews-section">
    <h2 class="text-xl font-bold mb-4">Product Reviews</h2>
    <div v-if="reviews.length">
      <div v-for="review in reviews" :key="review.id" class="review-item mb-4">
        <p class="font-semibold">{{ review.user }}</p>
        <p>{{ '★'.repeat(review.rating) }}</p>
        <p>{{ review.comment }}</p>
        <p class="text-sm text-gray-500">{{ new Date(review.created_at).toLocaleDateString() }}</p>
      </div>
    </div>
    <div v-else>
      <p>No reviews yet. Be the first to review this product!</p>
    </div>

    <div class="submit-review mt-6">
      <h3 class="text-lg font-semibold">Submit Your Review</h3>
      <form @submit.prevent="submitReview">
        <div class="mb-4">
          <label for="rating" class="block text-sm font-medium text-gray-700">Rating</label>
          <select v-model="newReview.rating" id="rating" class="mt-1 block w-full">
            <option v-for="n in 5" :key="n" :value="n">{{ n }} Star{{ n > 1 ? 's' : '' }}</option>
          </select>
        </div>
        <div class="mb-4">
          <label for="comment" class="block text-sm font-medium text-gray-700">Comment</label>
          <textarea v-model="newReview.comment" id="comment" rows="3" class="mt-1 block w-full"></textarea>
        </div>
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Submit Review</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    productId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      reviews: [],
      newReview: {
        rating: 5,
        comment: ''
      }
    };
  },
  methods: {
    fetchReviews() {
      axios.get(`/api/products/${this.productId}/reviews`)
        .then(response => {
          this.reviews = response.data.data;
        })
        .catch(error => {
          console.error("Error fetching reviews:", error);
        });
    },
    submitReview() {
      axios.post(`/api/products/${this.productId}/reviews`, this.newReview)
        .then(response => {
          this.reviews.push(response.data.data);
          this.newReview.rating = 5;
          this.newReview.comment = '';
        })
        .catch(error => {
          console.error("Error submitting review:", error);
        });
    }
  },
  mounted() {
    this.fetchReviews();
  }
};
</script>

<style scoped>
.reviews-section {
  max-width: 600px;
  margin: 0 auto;
}
.review-item {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}
</style>
