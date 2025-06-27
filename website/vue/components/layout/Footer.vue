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
              </ul>
            </div>
          </div>
          <div class="md:grid md:grid-cols-2 md:gap-8">
            <div class="md:grid md:grid-cols-2 md:gap-8">
              <div>
                <h3 class="text-sm font-semibold text-gray-400 tracking-wider uppercase">{{ $t('footer.sections.support') }}</h3>
                <ul class="mt-4 space-y-4">
                  <li><a href="/contact" class="text-base text-gray-300 hover:text-white">{{ $t('footer.links.contact') }}</a></li>
                  <li><router-link to="/faq" class="text-base text-gray-300 hover:text-white">{{ $t('footer.links.faq') }}</router-link></li>
                </ul>
                <a href="https://www.instagram.com/maisontruvra" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-white">
                  <span class="sr-only">Instagram</span>
                  <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12.315 2c-4.095 0-4.6.017-6.204.09-1.603.073-2.71.34-3.66.713-.975.38-1.743.9-2.508 1.664C.9 5.304.38 6.072.001 7.047c-.372.95-.64 2.057-.713 3.66C-1.258e-05 12.31 0 12.86 0 13.953s.017 1.643.09 3.247c.073 1.603.34 2.71.713 3.66.38.975.9 1.743 1.664 2.508.835.758 1.603 1.278 2.578 1.65.95.372 2.057.64 3.66.713 1.603.073 2.11.09 6.204.09s4.6-.017 6.204-.09c1.603-.073 2.71-.34 3.66-.713.975-.38 1.743-.9 2.508-1.664.765-.765 1.278-1.533 1.65-2.508.372-.95.64-2.057.713-3.66.073-1.603.09-2.11.09-6.204s-.017-4.6-.09-6.204c-.073-1.603-.34-2.71-.713-3.66-.38-.975-.9-1.743-1.664-2.508-.765-.765-1.533-1.278-2.508-1.65-.95-.372-2.057-.64-3.66-.713C16.915 2.017 16.41 2 12.315 2zM8.82 6.45c.44-.02.835.14 1.15.485.315.345.475.76.475 1.245a2.01 2.01 0 01-2.01 2.01 2.01 2.01 0 01-2.01-2.01c0-1.11.89-2.01 2-2.01.12 0 .24.01.36.03a1.94 1.94 0 01-.11-.535c0-.4.14-.73.42-1.01.28-.28.63-.42 1.05-.42.27 0 .52.06.73.18.21.12.39.29.53.51a1.94 1.94 0 01.11.535zm2.75 3.3c0-1.845 1.5-3.345 3.345-3.345S18.26 8.95 18.26 10.8s-1.5 3.345-3.345 3.345-3.345-1.5-3.345-3.345zm8.175-3.48a1.515 1.515 0 10-3.03 0 1.515 1.515 0 003.03 0zM12 15.3c-2.385 0-4.32-1.935-4.32-4.32s1.935-4.32 4.32-4.32 4.32 1.935 4.32 4.32-1.935 4.32-4.32 4.32z" clip-rule="evenodd" />
                  </svg>
                </a>

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
