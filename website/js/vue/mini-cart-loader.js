import { createApp } from 'vue';
import { createPinia } from 'pinia';
import MiniCart from './components/MiniCart.vue';

// Only mount the app if the container element exists on the page
const miniCartElement = document.getElementById('mini-cart');

if (miniCartElement) {
  const pinia = createPinia();
  const app = createApp(MiniCart);

  app.use(pinia);
  app.mount('#mini-cart');
}
