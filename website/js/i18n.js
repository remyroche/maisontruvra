import { getCurrentLanguage, setCurrentLanguage } from './utils/language';

// --- TRANSLATION DATA ---
const translations = {};

// --- LANGUAGE DETECTION & INITIALIZATION ---

/**
 * Detects the user's preferred language from the browser settings.
 * @returns {string} The detected language code (e.g., 'en', 'fr'). Defaults to 'en'.
 */
function detectLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.split('-')[0]; // Return the two-letter language code
}
import { getCurrentLanguage, setCurrentLanguage } from './utils/language';
import { translations as loadedTranslations } from 'virtual:translations';

// --- TRANSLATION DATA ---
const translations = loadedTranslations;

// --- LANGUAGE DETECTION & INITIALIZATION ---

/**
 * Detects the user's preferred language from the browser settings.
 * @returns {string} The detected language code (e.g., 'en', 'fr'). Defaults to 'en'.
 */
function detectLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.split('-')[0]; // Return the two-letter language code
}


// --- TRANSLATION FUNCTION ---

/**
 * Translates a given key into the currently selected language.
 * It supports nested keys in the format 'section.subsection.key'.
 * @param {string} key - The key to be translated.
 * @returns {string} The translated string, or the key itself if not found.
 */
export function t(key) {
    const lang = getCurrentLanguage();
    if (!translations[lang]) {
        return key; // Return the key if the language is not loaded
    }

    // Navigate through the nested object
    const keys = key.split('.');
    let result = translations[lang];
    for (const k of keys) {
        result = result[k];
        if (result === undefined) {
            return key; // Return the key if any part of it is not found
        }
    }

    return result;
}

// --- INITIALIZATION ---

/**
 * Initializes the i18n module.
 * It detects the language, loads the corresponding translation file,
 * and then updates all elements with the 'data-i18n' attribute.
 */
export async function initI18n() {
    let lang = getCurrentLanguage();
    if (!lang) {
        lang = detectLanguage();
        setCurrentLanguage(lang);
    }
    // No need to load translations, they are imported from the virtual module
    updateContent();
}

/**
 * Updates the content of all elements with a 'data-i18n' attribute.
 * It replaces the text content of these elements with the translated string.
 */
export function updateContent() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = t(key);
    });
}
