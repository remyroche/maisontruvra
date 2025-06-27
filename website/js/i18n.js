import { createI18n } from 'vue-i18n';

// Import combined translation files
import commonTranslations from './locales/common.json';
import faqTranslations from './locales/faq.json';

// A simple deep merge function to combine translation objects
const deepMerge = (target, ...sources) => {
  for (const source of sources) {
    for (const key in source) {
      // If the key exists in the target and both are objects, merge them recursively
      if (source[key] instanceof Object && key in target && target[key] instanceof Object) {
        deepMerge(target[key], source[key]);
      } else {
        // Otherwise, just assign the value
        target[key] = source[key];
      }
    }
  }
  return target;
};

// Assemble the final messages object by merging the page-specific translations
// for each language.
const messages = {
  en: deepMerge({}, commonTranslations.en, faqTranslations.en),
  fr: deepMerge({}, commonTranslations.fr, faqTranslations.fr),
};

const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: localStorage.getItem('preferredLanguage') || 'fr', // Default to French
  fallbackLocale: 'en',
  messages,
});

export default i18n;
