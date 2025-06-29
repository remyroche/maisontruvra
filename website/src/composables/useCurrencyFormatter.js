// website/src/composables/useCurrencyFormatter.js
// Description: A reusable composable for consistently formatting currency.

import { computed } from 'vue';

// Using Intl.NumberFormat is a modern, robust way to handle international currency formatting.
const formatter = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
});

export function useCurrencyFormatter() {
  /**
   * Formats a number into a French Euro currency string.
   * @param {number | string} value The numerical value to format.
   * @returns {string} The formatted currency string (e.g., "1 234,56 €").
   */
  const formatCurrency = (value) => {
    const numberValue = Number(value);
    if (isNaN(numberValue)) {
      return '';
    }
    return formatter.format(numberValue);
  };

  return { formatCurrency };
}
