import { reactive, toRefs } from 'vue';
import { setLocale as setVeeValidateLocale } from '@vee-validate/i18n';

// --- State ---
const state = reactive({
    currentLocale: localStorage.getItem('locale') || 'fr',
    translations: {},
});

// --- Private Methods ---
async function loadTranslations() {
    // Using Vite's glob import to get all locale files
    const localeModules = import.meta.glob('../locales/**/*.json');
    
    for (const path in localeModules) {
        const module = await localeModules[path]();
        const pathParts = path.split('/');
        // e.g., 'pages', 'account-dashboard.json'
        const group = pathParts[pathParts.length - 2]; 
        const key = pathParts[pathParts.length - 1].replace('.json', '');
        
        // Nest translations under their file key
        if (!state.translations[key]) {
            state.translations[key] = {};
        }
        
        for (const lang in module.default) {
            if (!state.translations[key][lang]) {
                state.translations[key][lang] = {};
            }
            Object.assign(state.translations[key][lang], module.default[lang]);
        }
    }
}

// --- Public API ---
const i18n = {
    // Method to install the plugin into a Vue app
    install(app) {
        app.config.globalProperties.$t = this.t.bind(this);
        app.config.globalProperties.$i18n = this;

        // Load translations when the app starts
        loadTranslations();
    },

    // Set the current language
    setLocale(locale) {
        if (!['fr', 'en'].includes(locale)) {
            console.warn(`Locale "${locale}" is not supported.`);
            return;
        }
        state.currentLocale = locale;
        localStorage.setItem('locale', locale);
        document.querySelector('html').setAttribute('lang', locale);
        
        // Also set the locale for VeeValidate messages
        setVeeValidateLocale(locale);
    },

    // Translate a key
    t(key) {
        const keys = key.split('.');
        if (keys.length < 2) {
            console.warn(`i18n key "${key}" is not specific enough. It should be in 'file.key' format.`);
            return key;
        }
        
        const fileKey = keys.shift();
        const translationKey = keys.join('.');
        
        try {
            const translation = state.translations[fileKey][state.currentLocale][translationKey];
            return translation || key;
        } catch (e) {
            // console.warn(`Translation not found for key: "${key}" in locale "${state.currentLocale}"`);
            return key;
        }
    },

    // Expose reactive state
    ...toRefs(state),
};

export default i18n;