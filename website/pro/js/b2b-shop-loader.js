import { createApp } from 'vue';
import { createPinia } from 'pinia';
import B2BShop from '../../js/vue/components/B2BShop.vue';

const shopElement = document.getElementById('b2b-shop-app');

if (shopElement) {
    const pinia = createPinia();
    const app = createApp(B2BShop);
    app.use(pinia);
    app.mount('#b2b-shop-app');
}
