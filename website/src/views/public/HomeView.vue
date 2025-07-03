<!-- website/src/views/public/HomeView.vue -->
<template>
  <div>
    <!-- Hero Section -->
    <section class="relative bg-brand-cream overflow-hidden">
      <div class="max-w-7xl mx-auto">
        <div class="relative z-10 pb-8 bg-brand-cream sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
          <svg class="hidden lg:block absolute right-0 inset-y-0 h-full w-48 text-brand-cream transform translate-x-1/2" fill="currentColor" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
            <polygon points="50,0 100,0 50,100 0,100" />
          </svg>

          <main class="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
            <div class="sm:text-center lg:text-left">
              <h1 class="text-4xl tracking-tight font-extrabold text-brand-dark-brown sm:text-5xl md:text-6xl">
                <span class="block xl:inline">L'excellence des</span>
                <span class="block text-brand-burgundy xl:inline">truffes françaises</span>
              </h1>
              <p class="mt-3 text-base text-gray-600 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                Depuis 1985, Maison Truvra sélectionne les meilleures truffes pour vous offrir une expérience gastronomique d'exception. Découvrez notre savoir-faire artisanal et nos produits d'exception.
              </p>
              <div class="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                <div class="rounded-md shadow">
                  <router-link to="/shop" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-brand-burgundy hover:bg-opacity-90 md:py-4 md:text-lg md:px-10">
                    Découvrir nos truffes
                  </router-link>
                </div>
                <div class="mt-3 sm:mt-0 sm:ml-3">
                  <router-link to="/notre-maison" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-brand-burgundy bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
                    Notre histoire
                  </router-link>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
      <div class="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
        <img class="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full" src="https://images.unsplash.com/photo-1587978744380-b9c148d4a65a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80" alt="Truffes noires d'exception" />
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="lg:text-center">
          <h2 class="text-base text-brand-burgundy font-semibold tracking-wide uppercase">Excellence</h2>
          <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Pourquoi choisir Maison Truvra ?
          </p>
          <p class="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Notre engagement pour la qualité et l'authenticité fait de nous le partenaire de confiance des plus grands chefs.
          </p>
        </div>
        <!-- ... features dl list from your template ... -->
      </div>
    </section>

    <!-- Products Preview -->
    <section class="bg-gray-50 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Nos produits d'exception
          </h2>
          <p class="mt-4 text-lg text-gray-600">
            Découvrez notre sélection de truffes et produits truffés
          </p>
        </div>
        <!-- This section can be populated dynamically with featured products -->
      </div>
    </section>

    <!-- --- DYNAMIC & PERSONALIZED SECTIONS --- -->
    
    <!-- Personalized Recommendations for logged-in users -->
    <PersonalizedRecommendations />

    <!-- Recently Viewed items -->
    <RecentlyViewed />
    
    <!-- ----------------------------------- -->

    <!-- CTA Section -->
    <section class="bg-brand-burgundy">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
        <h2 class="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          <span class="block">Prêt à découvrir l'exception ?</span>
          <span class="block text-brand-cream">Commandez dès aujourd'hui.</span>
        </h2>
        <div class="mt-8 flex lg:mt-0 lg:flex-shrink-0">
          <div class="inline-flex rounded-md shadow">
            <router-link to="/shop" class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-brand-burgundy bg-white hover:bg-gray-50">
              Boutique
            </router-link>
          </div>
          <div class="ml-3 inline-flex rounded-md shadow">
            <router-link to="/contact-b2c" class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-transparent border-white hover:bg-white hover:text-brand-burgundy">
              Nous contacter
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// Import the new components
import PersonalizedRecommendations from '@/components/products/PersonalizedRecommendations.vue';
import RecentlyViewed from '@/components/products/RecentlyViewed.vue';

// Other setup logic for the HomeView, such as fetching featured products, would go here.
// The personalization components handle their own data fetching internally.
</script>
