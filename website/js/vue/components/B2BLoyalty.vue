<template>
  <div>
    <h3 class="text-xl font-semibold mb-4 text-brand-burgundy">Niveaux et Bénéfices</h3>
    <div id="tiers-cards-container" class="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
      <div
        v-for="tier in mergedTiers"
        :key="tier.key"
        class="tier-card bg-white p-8 rounded-lg shadow-lg border-t-4 transition-all duration-300 flex flex-col"
        :class="[tier.style, { 'tier-card-active': userTier === tier.title }]"
      >
        <h3 class="font-serif text-2xl mb-2" :class="tier.titleColor || 'text-brand-dark-gray'">{{ tier.title }}</h3>
        <p class="font-sans text-brand-dark-gray mb-6 italic h-12">{{ tier.description }}</p>
        <ul class="text-left space-y-3 font-sans text-brand-dark-gray flex-grow">
          <li v-for="(benefit, index) in tier.benefits" :key="index" v-html="benefit"></li>
        </ul>
        <div v-if="userTier === tier.title" class="mt-6 text-center">
            <span class="font-bold text-white bg-indigo-600 rounded-full px-4 py-2">Votre Niveau Actuel</span>
        </div>
      </div>
    </div>
    <div id="ambassador-section" class="mt-12" v-if="ambassadorTier">
       <div class="max-w-4xl mx-auto text-center p-10 border-2 border-brand-gold rounded-xl bg-brand-cream">
            <h2 class="font-serif text-3xl text-brand-gold mb-2">{{ ambassadorTier.title }}</h2>
            <p class="font-sans text-brand-dark-gray mb-6 italic">{{ ambassadorTier.description }}</p>
            <p class="font-sans text-lg text-brand-dark-gray leading-relaxed" v-html="ambassadorTier.benefits[0]"></p>
        </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  /**
   * Array of tier data fetched from the backend.
   * Expected format: [{ name: 'Partenaire', discount_percentage: 10 }, ...]
   */
  tiers: {
    type: Array,
    required: true,
  },
  /**
   * The name of the current user's tier.
   */
  userTier: {
    type: String,
    default: '',
  }
});

// Hardcoded descriptive content for each tier.
const tierConfig = {
  collaborateur: {
    key: 'collaborateur',
    title: 'Collaborateur',
    description: "Le point de départ de l'innovation.",
    benefits: (discount) => [
        `Tarification professionnelle préférentielle (jusqu'à -${discount}%)`,
        'Accès complet au portail de commande B2B',
        'Support technique et culinaire dédié'
    ],
    style: 'border-gray-300'
  },
  partenaire: {
    key: 'partenaire',
    title: 'Partenaire',
    description: 'Concevoir de nouvelles structures de saveurs.',
    benefits: (discount) => [
        'Tous les bénéfices de <strong>Collaborateur</strong>',
        `Remise additionnelle de <strong>${discount}%</strong>`,
        'Allocation prioritaire des récoltes `Origine`',
        'Accès anticipé aux collections de l\'Atelier'
    ],
    style: 'border-brand-gold',
    titleColor: 'text-brand-burgundy'
  },
  associe: {
    key: 'associe',
    title: 'Associé',
    description: "Définir l'avenir de la gastronomie.",
    benefits: (discount) => [
        'Tous les bénéfices de <strong>Partenaire</strong>',
        `Remise additionnelle de <strong>${discount}%</strong>`,
        'Droit de premier refus sur l\'Avant-Garde',
        'Invitation à la table ronde R&D annuelle',
        'Potentiel de collaboration directe avec le labo'
    ],
    style: 'border-gray-300'
  },
  ambassadeur: {
    key: 'ambassadeur',
    title: 'Ambassadeur Maison Trüvra',
    description: 'Une distinction sur invitation uniquement.',
    benefits: (discount) => [
        `Le titre d'Ambassadeur est réservé aux chefs étoilés Michelin. Ils bénéficient d'un accès sans précédent à notre laboratoire, d'une remise de <strong>${discount}%</strong>, et de tous les avantages du niveau Partenaire, en reconnaissance de leur rôle essentiel dans la définition de l'avenir de la gastronomie.`
    ]
  }
};

// Map API names to our hardcoded config keys
const mapApiNameToConfigKey = {
  'Collaborateur': 'collaborateur',
  'Partenaire': 'partenaire',
  'Associé': 'associe',
  'Ambassadeur': 'ambassadeur',
};

// Merge dynamic data (from props) with static config.
const mergedTiers = computed(() => {
  return props.tiers
    .map(apiTier => {
      const configKey = mapApiNameToConfigKey[apiTier.name];
      if (configKey && tierConfig[configKey] && configKey !== 'ambassadeur') {
        const config = tierConfig[configKey];
        return {
          ...config,
          title: apiTier.name, // Always use the title from the API
          benefits: config.benefits(apiTier.discount_percentage)
        };
      }
      return null;
    })
    .filter(Boolean); // Remove any tiers that didn't match
});

const ambassadorTier = computed(() => {
    const apiTier = props.tiers.find(t => t.name === 'Ambassadeur');
    if (apiTier) {
        const config = tierConfig.ambassadeur;
        return {
            ...config,
            title: apiTier.name,
            benefits: config.benefits(apiTier.discount_percentage)
        };
    }
    return null;
});

</script>

<style scoped>
.tier-card-active {
  border-width: 2px;
  border-color: #4f46e5; /* indigo-600 */
  transform: scale(1.02);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
</style>
