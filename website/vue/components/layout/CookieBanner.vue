<template>
  <!--
    This banner is shown if the user has not yet made a choice regarding cookies.
    It is positioned at the bottom of the screen and overlays other content.
  -->
  <div
    v-if="showBanner"
    class="pointer-events-none fixed inset-x-0 bottom-0 px-6 pb-6"
  >
    <div
      class="pointer-events-auto mx-auto max-w-xl rounded-xl bg-white p-6 shadow-lg ring-1 ring-gray-900/10"
    >
      <p class="text-sm leading-6 text-gray-900">
        Ce site utilise des cookies pour améliorer votre expérience utilisateur et analyser le trafic. En cliquant sur "Accepter", vous consentez à notre utilisation des cookies. Vous pouvez en savoir plus en consultant notre
        <a href="/politique-confidentialite.html" class="font-semibold text-indigo-600">politique de confidentialité</a>.
      </p>
      <div class="mt-4 flex items-center gap-x-5">
        <button
          @click="acceptCookies"
          type="button"
          class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          Accepter
        </button>
        <button
          @click="declineCookies"
          type="button"
          class="rounded-md bg-gray-200 px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-300"
        >
          Refuser
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const COOKIE_CONSENT_KEY = 'cookie_consent';
const showBanner = ref(false);

/**
 * Checks for existing consent on component mount.
 * The banner is only shown if no consent has been previously recorded.
 */
onMounted(() => {
  const consent = localStorage.getItem(COOKIE_CONSENT_KEY);
  if (!consent) {
    showBanner.value = true;
  }
});

/**
 * Records the user's acceptance of cookies in localStorage and hides the banner.
 */
const acceptCookies = () => {
  localStorage.setItem(COOKIE_CONSENT_KEY, 'accepted');
  showBanner.value = false;
  // You could also dispatch an event here to enable analytics scripts
  // window.dispatchEvent(new CustomEvent('cookies-accepted'));
};

/**
 * Records the user's refusal of cookies in localStorage and hides the banner.
 */
const declineCookies = () => {
  localStorage.setItem(COOKIE_CONSENT_KEY, 'declined');
  showBanner.value = false;
};
</script>
