<template>
  <div class="relative">
    <div class="mx-auto max-w-7xl">
      <div class="relative z-10 pt-14 lg:w-full lg:max-w-2xl">
        <svg class="absolute inset-y-0 right-8 hidden h-full w-80 translate-x-1/2 transform fill-white lg:block" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
          <polygon points="0,0 90,0 50,100 0,100" />
        </svg>

        <div class="relative px-6 py-32 sm:py-40 lg:px-8 lg:py-56 lg:pr-0">
          <div class="mx-auto max-w-2xl lg:mx-0 lg:max-w-xl">
            <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">Donnez une âme à votre intérieur.</h1>
            <p class="mt-6 text-lg leading-8 text-gray-600">Découvrez notre sélection de mobilier et d'objets de décoration de seconde main, choisis avec soin pour leur histoire et leur caractère unique.</p>
            <div class="mt-10 flex items-center gap-x-6">
              <router-link to="/shop" class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Découvrir la collection</router-link>
              <router-link to="/le-journal" class="text-sm font-semibold leading-6 text-gray-900">Le Journal <span aria-hidden="true">→</span></router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="bg-gray-50 lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
      <img class="aspect-[3/2] object-cover lg:aspect-auto lg:h-full lg:w-full" src="https://images.unsplash.com/photo-1524758631624-e2822e304c36?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80" alt="Ambiance Maison Truv-ra">
    </div>
  </div>
</template>

<script setup>
// This view is primarily presentational.
</script>
