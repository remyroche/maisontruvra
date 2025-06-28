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
        <img class="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full" src="/images/hero-truffles.jpg" alt="Truffes noires d'exception" />
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

        <div class="mt-10">
          <dl class="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            <div class="relative">
              <dt>
                <div class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-brand-burgundy text-white">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p class="ml-16 text-lg leading-6 font-medium text-gray-900">Qualité garantie</p>
              </dt>
              <dd class="mt-2 ml-16 text-base text-gray-500">
                Chaque truffe est sélectionnée avec soin par nos experts pour garantir une qualité exceptionnelle.
              </dd>
            </div>

            <div class="relative">
              <dt>
                <div class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-brand-burgundy text-white">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <p class="ml-16 text-lg leading-6 font-medium text-gray-900">Livraison express</p>
              </dt>
              <dd class="mt-2 ml-16 text-base text-gray-500">
                Livraison rapide et sécurisée pour préserver la fraîcheur de nos produits d'exception.
              </dd>
            </div>

            <div class="relative">
              <dt>
                <div class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-brand-burgundy text-white">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <p class="ml-16 text-lg leading-6 font-medium text-gray-900">Savoir-faire artisanal</p>
              </dt>
              <dd class="mt-2 ml-16 text-base text-gray-500">
                Plus de 35 ans d'expertise dans la sélection et la préparation des truffes les plus raffinées.
              </dd>
            </div>

            <div class="relative">
              <dt>
                <div class="absolute flex items-center justify-center h-12 w-12 rounded-md bg-brand-burgundy text-white">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <p class="ml-16 text-lg leading-6 font-medium text-gray-900">Passion authentique</p>
              </dt>
              <dd class="mt-2 ml-16 text-base text-gray-500">
                Notre passion pour les truffes guide chacune de nos actions, de la récolte à votre assiette.
              </dd>
            </div>
          </dl>
        </div>
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

        <div class="mt-12 grid grid-cols-1 gap-y-10 sm:grid-cols-2 gap-x-6 lg:grid-cols-3 xl:gap-x-8">
          <!-- Product cards would be loaded here dynamically -->
          <div class="group relative">
            <div class="w-full min-h-80 bg-gray-200 aspect-w-1 aspect-h-1 rounded-md overflow-hidden group-hover:opacity-75 lg:h-80 lg:aspect-none">
              <img src="/images/truffe-noire.jpg" alt="Truffe noire du Périgord" class="w-full h-full object-center object-cover lg:w-full lg:h-full" />
            </div>
            <div class="mt-4 flex justify-between">
              <div>
                <h3 class="text-sm text-gray-700">
                  <span aria-hidden="true" class="absolute inset-0"></span>
                  Truffe noire du Périgord
                </h3>
                <p class="mt-1 text-sm text-gray-500">Extra</p>
              </div>
              <p class="text-sm font-medium text-gray-900">À partir de 89€</p>
            </div>
          </div>

          <div class="group relative">
            <div class="w-full min-h-80 bg-gray-200 aspect-w-1 aspect-h-1 rounded-md overflow-hidden group-hover:opacity-75 lg:h-80 lg:aspect-none">
              <img src="/images/huile-truffe.jpg" alt="Huile de truffe" class="w-full h-full object-center object-cover lg:w-full lg:h-full" />
            </div>
            <div class="mt-4 flex justify-between">
              <div>
                <h3 class="text-sm text-gray-700">
                  <span aria-hidden="true" class="absolute inset-0"></span>
                  Huile de truffe noire
                </h3>
                <p class="mt-1 text-sm text-gray-500">250ml</p>
              </div>
              <p class="text-sm font-medium text-gray-900">45€</p>
            </div>
          </div>

          <div class="group relative">
            <div class="w-full min-h-80 bg-gray-200 aspect-w-1 aspect-h-1 rounded-md overflow-hidden group-hover:opacity-75 lg:h-80 lg:aspect-none">
              <img src="/images/brisures-truffe.jpg" alt="Brisures de truffe" class="w-full h-full object-center object-cover lg:w-full lg:h-full" />
            </div>
            <div class="mt-4 flex justify-between">
              <div>
                <h3 class="text-sm text-gray-700">
                  <span aria-hidden="true" class="absolute inset-0"></span>
                  Brisures de truffe
                </h3>
                <p class="mt-1 text-sm text-gray-500">50g</p>
              </div>
              <p class="text-sm font-medium text-gray-900">32€</p>
            </div>
          </div>
        </div>

        <div class="mt-12 text-center">
          <router-link to="/shop" class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-brand-burgundy hover:bg-opacity-90">
            Voir tous nos produits
            <svg class="ml-2 -mr-1 w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </router-link>
        </div>
      </div>
    </section>

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
// This view is primarily presentational.
</script>