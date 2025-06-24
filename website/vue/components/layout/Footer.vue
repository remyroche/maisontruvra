<template>
  <footer class="bg-gray-50" aria-labelledby="footer-heading">
    <h2 id="footer-heading" class="sr-only">Footer</h2>
    <div class="mx-auto max-w-7xl px-4 pt-16 pb-8 sm:px-6 lg:px-8 lg:pt-24">
      <div class="xl:grid xl:grid-cols-3 xl:gap-8">
        <div class="grid grid-cols-2 gap-8 xl:col-span-2">
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Explorer</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><router-link to="/shop" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Boutique</router-link></li>
                <li><a href="/notre-maison" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Notre Maison</a></li>
                <li><a href="/le-journal" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Le Journal</a></li>
                <li><a href="/charte-qualite" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Charte Qualité</a></li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Professionnels</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><a href="/professionnels" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Espace Pro</a></li>
                <li><a href="/pro/register" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Devenir Partenaire</a></li>
                <li><a href="/pro/contact" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Contact Pro</a></li>
              </ul>
            </div>
          </div>
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Aide</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><a href="/contact" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Contact</a></li>
                <li><a href="/faq" class="text-sm leading-6 text-gray-600 hover:text-gray-900">FAQ</a></li>
                <li><a href="/livraison" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Livraison & Retours</a></li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Légal</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><a href="/politique-confidentialite" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Confidentialité</a></li>
                <li><a href="/cgv" class="text-sm leading-6 text-gray-600 hover:text-gray-900">CGV</a></li>
                <li><a href="#" @click.prevent="openCookieSettings" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Préférences cookies</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div class="mt-10 xl:mt-0">
          <Newsletter />
        </div>
      </div>
      <div class="mt-16 border-t border-gray-900/10 pt-8 sm:mt-20 lg:mt-24 lg:flex lg:items-center lg:justify-between">
        <div>
          <h3 class="text-sm font-semibold leading-6 text-gray-900">Suivez-nous</h3>
          <div class="mt-6 flex gap-x-4"><!-- Social links here --></div>
        </div>
        <div class="mt-8 lg:mt-0 lg:flex-shrink-0 lg:flex-grow">
          <p class="text-sm leading-6 text-gray-500 lg:text-right">© {{ new Date().getFullYear() }} Maison Truv-ra. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import Newsletter from './Newsletter.vue';

function openCookieSettings() {
  if (window.CCM) {
    window.CCM.openWidget();
  } else {
    alert("Le gestionnaire de cookies n'est pas disponible.");
  }
}
</script>
