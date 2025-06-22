<template>
  <footer class="bg-dark-brown text-cream">
    <div class="container mx-auto px-6 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-lg font-serif uppercase tracking-wider text-white">Maison Trüvra</h3>
          <p class="mt-4 text-sm text-gray-300">L'excellence de la truffe, de notre terroir à votre table.</p>
        </div>
        <!-- Links -->
        <div>
          <h3 class="text-lg font-serif uppercase tracking-wider text-white">Navigation</h3>
          <ul class="mt-4 space-y-2 text-sm">
            <li><router-link :to="{ name: 'catalogue' }" class="hover:text-gold transition-colors">Nos Produits</router-link></li>
            <li><a href="#" class="hover:text-gold transition-colors">Notre Histoire</a></li>
            <li><a href="#" class="hover:text-gold transition-colors">Contact</a></li>
            <li><router-link :to="{ name: 'pro-login' }" class="hover:text-gold transition-colors">Espace Professionnel</router-link></li>
          </ul>
        </div>
        <!-- Legal -->
        <div>
          <h3 class="text-lg font-serif uppercase tracking-wider text-white">Légal</h3>
          <ul class="mt-4 space-y-2 text-sm">
            <li><a href="#" class="hover:text-gold transition-colors">Conditions Générales de Vente</a></li>
            <li><a href="#" class="hover:text-gold transition-colors">Mentions Légales</a></li>
            <li><a href="#" class="hover:text-gold transition-colors">Politique de Confidentialité</a></li>
          </ul>
        </div>
        <!-- Newsletter -->
        <div>
          <h3 class="text-lg font-serif uppercase tracking-wider text-white">Newsletter</h3>
          <p class="mt-4 text-sm text-gray-300">Recevez nos offres exclusives et actualités.</p>
          <form @submit.prevent class="mt-4 flex">
            <input type="email" placeholder="Votre email" class="input-field w-full text-sm !py-2 !px-3 rounded-r-none" />
            <button type="submit" class="btn btn-primary rounded-l-none !py-2 !px-4">S'inscrire</button>
          </form>
        </div>
      </div>
      <div class="mt-12 border-t border-white border-opacity-20 pt-8 text-center text-sm text-gray-400">
        &copy; {{ new Date().getFullYear() }} Maison Trüvra. Tous droits réservés.
      </div>
    </div>
  </footer>
</template>

<script setup>
// No script logic needed for this basic footer
</script>