<template>
  <footer class="bg-gray-100 text-gray-700">
    <div class="container mx-auto px-6 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <h3 class="font-bold uppercase">Maison Trüvra</h3>
          <p class="mt-4 text-sm">L'art de la truffe, une tradition familiale.</p>
        </div>
        <div>
          <h3 class="font-bold uppercase">Service Client</h3>
          <nav class="mt-4 space-y-2 text-sm">
            <a href="/contact.html" class="hover:text-black transition-colors duration-300">Nous Contacter</a><br>
            <a href="/faq.html" class="hover:text-black transition-colors duration-300">FAQ</a><br>
            <a href="/livraison.html" class="hover:text-black transition-colors duration-300">Livraison & Retours</a>
          </nav>
        </div>
        <div>
          <h3 class="font-bold uppercase">Informations</h3>
          <nav class="mt-4 space-y-2 text-sm">
            <a href="/mentions-legales.html" class="hover:text-black transition-colors duration-300">Mentions Légales</a><br>
            <a href="/cgv.html" class="hover:text-black transition-colors duration-300">Conditions Générales de Vente</a><br>
            <a href="/politique-confidentialite.html" class="hover:text-black transition-colors duration-300">Politique de Confidentialité</a>
          </nav>
        </div>
        <div>
          <h3 class="font-bold uppercase">Devenez un initié de la truffe</h3>
          <p class="mt-4 text-sm">Recevez nos secrets et offres exclusives.</p>
          <form class="mt-4 flex" @submit.prevent="submitNewsletter">
            <input type="email" placeholder="Votre email" class="w-full px-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-gray-500">
            <button type="submit" class="bg-black text-white px-4 py-2 rounded-r-md hover:bg-gray-800 transition-colors duration-300">S'inscrire</button>
          </form>
        </div>
      </div>
      <div class="mt-12 pt-8 border-t border-gray-300 flex flex-col md:flex-row justify-between items-center">
          <div class="flex space-x-4 mb-4 md:mb-0">
            <a href="#" aria-label="Facebook"><img src="https://placehold.co/24x24/000000/FFFFFF?text=F" alt="Facebook"></a>
            <a href="#" aria-label="Instagram"><img src="https://placehold.co/24x24/000000/FFFFFF?text=I" alt="Instagram"></a>
            <a href="#" aria-label="Twitter"><img src="https://placehold.co/24x24/000000/FFFFFF?text=T" alt="Twitter"></a>
          </div>
          <div class="flex items-center space-x-2 mb-4 md:mb-0">
              <img src="https://placehold.co/40x25/e0e0e0/000000?text=VISA" alt="Visa">
              <img src="https://placehold.co/40x25/e0e0e0/000000?text=MC" alt="Mastercard">
              <img src="https://placehold.co/40x25/e0e0e0/000000?text=PP" alt="PayPal">
              <img src="https://placehold.co/40x25/e0e0e0/000000?text=AP" alt="Apple Pay">
          </div>
          <p class="text-sm">&copy; {{ new Date().getFullYear() }} Maison Trüvra. Tous droits réservés.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
// For newsletter submission, you would add a method here:
const submitNewsletter = () => {
  console.log('Newsletter form submitted');
  // Add your logic to handle newsletter subscription, e.g., an API call
};
</script>
