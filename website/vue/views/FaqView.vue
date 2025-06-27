<template>
  <div class="bg-gray-50">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:py-16 sm:px-6 lg:px-8">
      <div class="max-w-3xl mx-auto">
        <h2 class="text-center text-3xl font-extrabold text-gray-900 sm:text-4xl">
          {{ $t('faq.title') }}
        </h2>
        <p class="text-center mt-4 text-lg text-gray-600">
          {{ $t('faq.subtitle') }}
        </p>
        
        <div class="mt-12 space-y-8">
          <!-- FAQ Section -->
          <div v-for="(section, sectionIndex) in faqSections" :key="section.title">
            <h3 class="text-xl font-semibold text-gray-900 mb-4 border-l-4 border-primary pl-4">
              {{ $t(section.title) }}
            </h3>
            <div class="space-y-1">
              <div v-for="(item, itemIndex) in section.items" :key="item.q" class="border-t">
                <button @click="toggleItem(sectionIndex, itemIndex)" class="w-full flex justify-between items-center text-left py-4 px-2 hover:bg-gray-100 focus:outline-none"
                        :class="item.open ? 'text-primary' : 'text-gray-800'">
                  <span class="font-medium">{{ $t(item.q) }}</span>
                  <span class="ml-6 h-7 flex items-center">
                    <svg class="h-6 w-6 transform transition-transform duration-300" :class="{'rotate-180 text-primary': item.open, 'text-gray-400': !item.open}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </button>
                <transition
                  enter-active-class="transition ease-out duration-200"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-100"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <div v-if="item.open" class="pb-4 px-2">
                    <p class="text-base text-gray-600" v-html="$t(item.a)"></p>
                  </div>
                </transition>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const faqSections = ref([
  {
    title: 'faq.sections.ordering.title',
    items: [
      { q: 'faq.sections.ordering.q1', a: 'faq.sections.ordering.a1', open: false },
      { q: 'faq.sections.ordering.q2', a: 'faq.sections.ordering.a2', open: false },
      { q: 'faq.sections.ordering.q3', a: 'faq.sections.ordering.a3', open: false },
    ],
  },
  {
    title: 'faq.sections.shipping.title',
    items: [
      { q: 'faq.sections.shipping.q1', a: 'faq.sections.shipping.a1', open: false },
      { q: 'faq.sections.shipping.q2', a: 'faq.sections.shipping.a2', open: false },
      { q: 'faq.sections.shipping.q3', a: 'faq.sections.shipping.a3', open: false },
    ],
  },
  {
    title: 'faq.sections.products.title',
    items: [
      { q: 'faq.sections.products.q1', a: 'faq.sections.products.a1', open: false },
      { q: 'faq.sections.products.q2', a: 'faq.sections.products.a2', open: false },
    ],
  },
  {
    title: 'faq.sections.loyalty.title',
    items: [
      { q: 'faq.sections.loyalty.q1', a: 'faq.sections.loyalty.a1', open: false },
      { q: 'faq.sections.loyalty.q2', a: 'faq.sections.loyalty.a2', open: false },
      { q: 'faq.sections.loyalty.q3', a: 'faq.sections.loyalty.a3', open: false },
    ],
  },
]);

const toggleItem = (sectionIndex, itemIndex) => {
  const isOpen = faqSections.value[sectionIndex].items[itemIndex].open;
  // Optional: Close all other items when one is opened for a cleaner look
  // faqSections.value.forEach(section => section.items.forEach(item => item.open = false));
  faqSections.value[sectionIndex].items[itemIndex].open = !isOpen;
};
</script>
