
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

// Custom password rule matching backend requirements
defineRule('password', (value) => {
  if (!value) return 'Le mot de passe est requis';
  if (value.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères';
  if (!/(?=.*[a-z])/.test(value)) return 'Le mot de passe doit contenir au moins une minuscule';
  if (!/(?=.*[A-Z])/.test(value)) return 'Le mot de passe doit contenir au moins une majuscule';
  if (!/(?=.*\d)/.test(value)) return 'Le mot de passe doit contenir au moins un chiffre';
  if (!/(?=.*[@$!%*?&])/.test(value)) return 'Le mot de passe doit contenir au moins un caractère spécial';
  return true;
});

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
