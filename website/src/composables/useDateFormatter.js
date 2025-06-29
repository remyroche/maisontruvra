// website/src/composables/useDateFormatter.js
// Description: A reusable composable for consistently formatting dates.

import { computed } from 'vue';

// Using Intl.DateTimeFormat is best practice for date formatting.
const dateFormatter = new Intl.DateTimeFormat('fr-FR', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});

export function useDateFormatter() {
  /**
   * Formats a date string or Date object into a readable format.
   * @param {string | Date} dateStr The date string (ISO format) or Date object.
   * @returns {string} The formatted date string (e.g., "29 juin 2025").
   */
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      return dateFormatter.format(new Date(dateStr));
    } catch (error) {
      console.error('Could not format date:', dateStr, error);
      return '';
    }
  };

  return { formatDate };
}