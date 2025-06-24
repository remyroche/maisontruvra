
<template>
  <div>
    <div class="relative bg-gray-900 text-white">
      <img src="https://placehold.co/1600x800/1a202c/718096?text=Cuisine+Gastronomique" 
           alt="Chef cuisinant avec des produits à la truffe" 
           class="absolute h-full w-full object-cover opacity-30">
      <div class="relative container mx-auto px-6 py-24 text-center">
        <h1 class="text-4xl md:text-6xl font-bold leading-tight">L'excellence de la truffe, <br>pour les professionnels exigeants</h1>
        <p class="mt-4 text-lg md:text-xl max-w-3xl mx-auto text-gray-300">Accédez à notre catalogue, bénéficiez de tarifs préférentiels et offrez à votre clientèle l'expérience inoubliable de la Maison Trüvra.</p>
        <a href="#register-section" class="mt-8 inline-block bg-white text-black font-bold py-3 px-8 rounded-md hover:bg-gray-200 transition-colors duration-300">Créer votre compte pro</a>
      </div>
    </div>

    <section class="bg-white py-20">
      <div class="container mx-auto px-6">
        <h2 class="text-3xl font-bold text-center mb-12 text-gray-800">Les avantages de votre compte professionnel</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8 text-center">
          <div class="flex flex-col items-center">
            <div class="bg-gray-100 rounded-full p-4 mb-4">
              <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            </div>
            <h3 class="font-bold text-lg text-gray-800">Tarifs préférentiels</h3>
            <p class="text-gray-600 text-sm">Accédez à une grille tarifaire exclusive pour maximiser votre rentabilité.</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="bg-gray-100 rounded-full p-4 mb-4">
              <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h3 class="font-bold text-lg text-gray-800">Livraison sur-mesure</h3>
            <p class="text-gray-600 text-sm">Bénéficiez d'options adaptées à vos impératifs (créneau horaire, transporteur...).</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="bg-gray-100 rounded-full p-4 mb-4">
              <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>
            </div>
            <h3 class="font-bold text-lg text-gray-800">Produits sur-mesure</h3>
            <p class="text-gray-600 text-sm">Contactez-nous pour développer des créations uniques pour votre marque.</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="bg-gray-100 rounded-full p-4 mb-4">
              <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            </div>
            <h3 class="font-bold text-lg text-gray-800">Passeport produit</h3>
            <p class="text-gray-600 text-sm">Une traçabilité totale via QR code pour garantir l'origine et la qualité.</p>
          </div>
          <div class="flex flex-col items-center">
            <div class="bg-gray-100 rounded-full p-4 mb-4">
              <svg class="h-8 w-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a2 2 0 01-2-2V4a2 2 0 012-2h8a2 2 0 012 2v4z"></path></svg>
            </div>
            <h3 class="font-bold text-lg text-gray-800">Support dédié</h3>
            <p class="text-gray-600 text-sm">Un interlocuteur privilégié pour vous conseiller et simplifier vos commandes.</p>
          </div>
        </div>
      </div>
    </section>
    
    <section id="register-section" class="bg-gray-50 py-20">
      <div class="container mx-auto px-6">
        <div class="lg:grid lg:grid-cols-2 lg:gap-12 items-center">
          <div>
            <h2 class="text-3xl font-bold text-gray-800">Rejoignez notre réseau de partenaires</h2>
            <p class="mt-4 text-gray-600">En quelques étapes simples, accédez à tous les avantages de l'espace professionnel. Remplissez le formulaire, notre équipe validera votre inscription sous 48h.</p>
            <h3 class="font-semibold mt-8 mb-4 text-gray-800">Notre offre s'adresse aux :</h3>
            <ul class="list-disc list-inside space-y-2 text-gray-700">
              <li>Épiceries fines & Delicatessen</li>
              <li>Restaurants gastronomiques & Chefs</li>
              <li>Hôtels de luxe & Conciergeries</li>
              <li>Revendeurs et distributeurs spécialisés</li>
            </ul>
            <div class="mt-8">
              <router-link to="/pro/faq-pro" class="font-bold text-black hover:underline">Une question ? Consultez notre FAQ Professionnels &rarr;</router-link>
            </div>
          </div>
          
          <div class="mt-12 lg:mt-0">
            <div class="bg-white p-8 rounded-lg shadow-lg">
              <AuthPortal />
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import AuthPortal from '../components/AuthPortal.vue'; // Adjust path if needed

// No specific script logic beyond component import, assuming AuthPortal handles its own state and actions.
</script>

<style scoped>
/* Add any component-specific styles here if necessary */
</style>
