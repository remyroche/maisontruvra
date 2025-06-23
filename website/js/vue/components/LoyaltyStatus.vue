<template>
  <div>
    <h3 class="text-xl font-semibold mb-4 text-brand-burgundy">Votre Statut Actuel</h3>
    <div v-if="status" class="bg-indigo-50 p-6 rounded-lg text-center">
      <p class="text-lg text-indigo-800">Solde de points</p>
      <p class="text-6xl font-bold text-indigo-600 my-2">{{ status.points?.toLocaleString() || 0 }}</p>
      <div class="mt-4">
          <p class="font-semibold">Votre Niveau: 
            <span class="text-indigo-600 font-bold">{{ status.tier || 'Standard' }}</span>
          </p>
      </div>
    </div>
    <div v-else class="bg-gray-100 p-6 rounded-lg text-center">
        <p class="text-gray-500">Les informations de fidélité sont en cours de chargement...</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  /**
   * The user's loyalty status object, fetched from the API.
   * @type {{ points: number, tier: string } | null}
   */
  status: {
    type: Object,
    default: () => null
  }
});
</script>

<style scoped>
/* Add any component-specific styles here */
</style>

