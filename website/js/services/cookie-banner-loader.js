import { createApp } from 'vue';
import CookieBanner from '../vue/components/layout/CookieBanner.vue';

// Mount the CookieBanner component into its placeholder div.
const cookieBannerContainer = document.getElementById('cookie-banner-container');
if (cookieBannerContainer) {
    const app = createApp(CookieBanner);
    app.mount(cookieBannerContainer);
}
