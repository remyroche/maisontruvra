<template>
  <footer class="bg-gray-800" aria-labelledby="footer-heading">
    <h2 id="footer-heading" class="sr-only">Footer</h2>
    <div class="mx-auto max-w-7xl px-4 pt-16 pb-8 sm:px-6 lg:px-8 lg:pt-24">
      <div class="xl:grid xl:grid-cols-3 xl:gap-8">
        <div class="grid grid-cols-2 gap-8 xl:col-span-2">
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-white">Explorer</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/products.html" class="text-sm leading-6 text-gray-300 hover:text-white">Boutique</a>
                </li>
                 <li>
                  <a href="/notre-maison.html" class="text-sm leading-6 text-gray-300 hover:text-white">Notre Maison</a>
                </li>
                <li>
                  <a href="/le-journal.html" class="text-sm leading-6 text-gray-300 hover:text-white">Le Journal</a>
                </li>
                 <li>
                  <a href="/charte-qualite.html" class="text-sm leading-6 text-gray-300 hover:text-white">Charte Qualité</a>
                </li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-white">Professionnels</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/professionnels.html" class="text-sm leading-6 text-gray-300 hover:text-white">Espace Pro</a>
                </li>
                <li>
                  <a href="/pro/register.html" class="text-sm leading-6 text-gray-300 hover:text-white">Devenir Partenaire</a>
                </li>
                 <li>
                  <a href="/pro/contact.html" class="text-sm leading-6 text-gray-300 hover:text-white">Contact Pro</a>
                </li>
              </ul>
            </div>
          </div>
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-white">Aide</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/contact.html" class="text-sm leading-6 text-gray-300 hover:text-white">Contact</a>
                </li>
                <li>
                  <a href="/faq.html" class="text-sm leading-6 text-gray-300 hover:text-white">FAQ</a>
                </li>
                <li>
                  <a href="/livraison.html" class="text-sm leading-6 text-gray-300 hover:text-white">Livraison & Retours</a>
                </li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-white">Légal</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/politique-confidentialite.html" class="text-sm leading-6 text-gray-300 hover:text-white">Confidentialité</a>
                </li>
                <li>
                  <a href="/cgv.html" class="text-sm leading-6 text-gray-300 hover:text-white">CGV</a>
                </li>
                 <li>
                  <a href="#" @click.prevent="openCookieSettings" class="text-sm leading-6 text-gray-300 hover:text-white">Préférences cookies</a>
                </li>
              </ul>
            </div>
          </div>
        </di<template>
  <footer class="bg-gray-800" aria-labelledby="footer-heading">
    <h2 id="footer-heading" class="sr-only">Footer</h2>
    <div class="mx-auto max-w-7xl px-4 pt-16 pb-8 sm:px-6 lg:px-8 lg:pt-24">
      <div class="xl:grid xl:grid-cols-3 xl:gap-8">
        <div class="grid grid-cols-2 gap-8 xl:col-span-2">
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-white">Mon Espace Pro</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><router-link to="/pro/dashboard" class="text-sm leading-6 text-gray-300 hover:text-white">Tableau de bord</router-link></li>
                <li><router-link to="/pro/shop" class="text-sm leading-6 text-gray-300 hover:text-white">Commander</router-link></li>
                <li><router-link to="/pro/orders" class="text-sm leading-6 text-gray-300 hover:text-white">Mes Commandes</router-link></li>
                <li><router-link to="/pro/invoices" class="text-sm leading-6 text-gray-300 hover:text-white">Mes Factures</router-link></li>
                <li><router-link to="/pro/profile" class="text-sm leading-6 text-gray-300 hover:text-white">Mon Profil</router-link></li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-white">Ressources</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><router-link to="/contact-b2b" class="text-base text-gray-300 hover:text-white">Contact</router-link></li>
                 <li><a href="/faq" class="text-sm leading-6 text-gray-300 hover:text-white">FAQ</a></li>
              </ul>
            </div>
          </div>
          <div class="md:grid md:grid-cols-2 md:gap-8">
             <div>
              <h3 class="text-sm font-semibold leading-6 text-white">Légal</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li><a href="/politique-confidentialite" class="text-sm leading-6 text-gray-300 hover:text-white">Confidentialité</a></li>
                <li><a href="/cgv" class="text-sm leading-6 text-gray-300 hover:text-white">CGV</a></li>
                 <li><a href="#" @click.prevent="openCookieSettings" class="text-sm leading-6 text-gray-300 hover:text-white">Préférences cookies</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div class="mt-10 xl:mt-0">
          <B2BNewsletter />
        </div>
      </div>
      <div class="mt-16 border-t border-white/10 pt-8 sm:mt-20 lg:mt-24 lg:flex lg:items-center lg:justify-between">
        <div>
          <h3 class="text-sm font-semibold leading-6 text-white">Suivez-nous</h3>
          <div class="mt-6 flex gap-x-4"><!-- Social links here --></div>
        </div>
        <div class="mt-8 lg:mt-0 lg:flex-shrink-0 lg:flex-grow">
          <p class="text-sm leading-6 text-gray-300 lg:text-right">© {{ new Date().getFullYear() }} Maison Truv-ra. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import B2BNewsletter from './B2BNewsletter.vue';

function openCookieSettings() {
  if (window.CCM) {
    window.CCM.openWidget();
  } else {
    alert("Le gestionnaire de cookies n'est pas disponible.");
  }
}
</script>
