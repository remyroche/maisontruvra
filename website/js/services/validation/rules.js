
/**
 * Frontend validation rules that mirror backend validation
 */
import { defineRule } from 'vee-validate';
import { required, email, min, max, confirmed } from '@vee-validate/rules';

// Define standard rules
defineRule('required', required);
defineRule('email', email);
defineRule('min', min);
defineRule('max', max);
defineRule('confirmed', confirmed);

// --- IMPLEMENTATION: Enhanced Password Validation ---
// These rules are defined to mirror the backend policy in `config.py`.

export const required = value => (value ? true : 'This field is required');

export const email = value => {
  if (!value) return true; // Don't validate if empty, let `required` rule handle that.
  const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;
  return regex.test(value) ? true : 'Must be a valid email';
};

// New Password Rules
export const minLength = (value, [limit]) => {
  if (!value) return true;
  return value.length >= limit ? true : `Must be at least ${limit} characters`;
};

export const hasUppercase = value => {
    if (!value) return true;
    return /[A-Z]/.test(value) ? true : 'Must contain at least one uppercase letter';
};

export const hasLowercase = value => {
    if (!value) return true;
    return /[a-z]/.test(value) ? true : 'Must contain at least one lowercase letter';
};

export const hasDigit = value => {
    if (!value) return true;
    return /\d/.test(value) ? true : 'Must contain at least one number';
};

export const hasSpecialChar = value => {
    if (!value) return true;
    return /[\W_]/.test(value) ? true : 'Must contain at least one special character';
};


// --- IMPLEMENTATION: Admin Form Edge Case Rules ---

export const isPositiveNumber = value => {
  if (value === null || value === undefined || value === '') return true;
  const num = Number(value);
  return !isNaN(num) && num > 0 ? true : 'Must be a positive number';
};

export const isNonNegativeInteger = value => {
  if (value === null || value === undefined || value === '') return true;
  const num = Number(value);
  return !isNaN(num) && Number.isInteger(num) && num >= 0 ? true : 'Must be a non-negative integer';
};
// Phone number validation
defineRule('phone', (value) => {
  if (!value) return true; // Optional field
  const phoneRegex = /^(?:\+33|0)[1-9](?:[0-9]{8})$/;
  if (!phoneRegex.test(value)) return 'Veuillez saisir un numéro de téléphone français valide';
  return true;
});

// SIRET validation for B2B
defineRule('siret', (value) => {
  if (!value) return true; // Optional field
  const siretRegex = /^\d{14}$/;
  if (!siretRegex.test(value)) return 'Le SIRET doit contenir exactement 14 chiffres';
  return true;
});

// Postal code validation
defineRule('postal_code', (value) => {
  if (!value) return 'Le code postal est requis';
  const postalRegex = /^\d{5}$/;
  if (!postalRegex.test(value)) return 'Le code postal doit contenir 5 chiffres';
  return true;
});
