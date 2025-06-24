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
                <li>
                  <a href="/products.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Boutique</a>
                </li>
                 <li>
                  <a href="/notre-maison.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Notre Maison</a>
                </li>
                <li>
                  <a href="/le-journal.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Le Journal</a>
                </li>
                 <li>
                  <a href="/charte-qualite.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Charte Qualité</a>
                </li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Professionnels</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/professionnels.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Espace Pro</a>
                </li>
                <li>
                  <a href="/pro/register.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Devenir Partenaire</a>
                </li>
                 <li>
                  <a href="/pro/contact.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Contact Pro</a>
                </li>
              </ul>
            </div>
          </div>
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div>
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Aide</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/contact.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Contact</a>
                </li>
                <li>
                  <a href="/faq.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">FAQ</a>
                </li>
                <li>
                  <a href="/livraison.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Livraison & Retours</a>
                </li>
              </ul>
            </div>
            <div class="mt-10 md:mt-0">
              <h3 class="text-sm font-semibold leading-6 text-gray-900">Légal</h3>
              <ul role="list" class="mt-6 space-y-4">
                <li>
                  <a href="/politique-confidentialite.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Confidentialité</a>
                </li>
                <li>
                  <a href="/cgv.html" class="text-sm leading-6 text-gray-600 hover:text-gray-900">CGV</a>
                </li>
                 <li>
                  <a href="#" @click.prevent="openCookieSettings" class="text-sm leading-6 text-gray-600 hover:text-gray-900">Préférences cookies</a>
                </li>
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
          <div class="mt-6 flex gap-x-4">
            <!-- Social links here -->
            <a href="#" class="text-gray-400 hover:text-gray-500">
              <span class="sr-only">Instagram</span>
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.315 2c-4.02.094-5.55.584-6.817 1.096A5.38 5.38 0 002.095 6.817C1.583 8.084 1.094 9.615 1.001 13.635c-.093 4.02.4 5.55 1.095 6.817a5.38 5.38 0 003.704 3.704c1.267.512 2.797 1.001 6.817 1.095 4.02-.094 5.55-.584 6.817-1.095a5.38 5.38 0 003.704-3.704c.512-1.267 1.001-2.797 1.095-6.817-.094-4.02-.584-5.55-1.096-6.817a5.38 5.38 0 00-3.703-3.704C17.865 2.583 16.335 2.094 12.315 2zm-1.03 1.802c3.927-.085 5.242.383 6.38 1.002a3.57 3.57 0 012.168 2.168c.62 1.138 1.087 2.453 1.002 6.38-.085 3.927-.383 5.242-1.002 6.38a3.57 3.57 0 01-2.168 2.168c-1.138.62-2.453 1.087-6.38 1.002-3.927.085-5.242-.383-6.38-1.002a3.57 3.57 0 01-2.168-2.168c-.62-1.138-1.087-2.453-1.002-6.38.085-3.927.383-5.242 1.002-6.38a3.57 3.57 0 012.168-2.168c1.138-.62 2.453-1.087 6.38-1.002zM12 7.875a4.125 4.125 0 100 8.25 4.125 4.125 0 000-8.25zM12 14.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5zm5.125-7.125a.938.938 0 100-1.875.938.938 0 000 1.875z" clip-rule="evenodd" />
              </svg>
            </a>
          </div>
        </div>
        <div class="mt-8 lg:mt-0 lg:flex-shrink-0 lg:flex-grow">
          <p class="text-sm leading-6 text-gray-500 lg:text-right">© 2024 Maison Truv-ra. Tous droits réservés.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import Newsletter from './Newsletter.vue';

/**
 * Opens the cookie consent manager settings.
 * This assumes you have a cookie consent library initialized that provides such a function.
 */
function openCookieSettings() {
  if (window.CCM) {
    window.CCM.openWidget();
  } else {
    alert("Le gestionnaire de cookies n'est pas disponible.");
  }
}
</script>
