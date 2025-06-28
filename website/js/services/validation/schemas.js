import * as yup from 'yup';

// Note: You will need to add 'yup' and 'vee-validate' to your package.json
// npm install yup vee-validate

export const registrationSchema = yup.object({
  first_name: yup.string().required('First name is required').min(2, 'First name must be at least 2 characters'),
  last_name: yup.string().required('Last name is required').min(2, 'Last name must be at least 2 characters'),
  email: yup.string().required('Email is required').email('Must be a valid email'),
  password: yup.string().required('Password is required').min(8, 'Password must be at least 8 characters'),
  confirm_password: yup.string()
    .oneOf([yup.ref('password'), null], 'Passwords must match')
    .required('Password confirmation is required'),
  agree_to_terms: yup.boolean().oneOf([true], 'You must accept the terms and conditions'),
});

export const loyaltyTierSchema = yup.object({
  name: yup.string().required('Tier name is required'),
  min_spend: yup.number()
    .typeError('Minimum spend must be a number')
    .required('Minimum spend is required')
    .min(0, 'Minimum spend cannot be negative'),
  points_per_euro: yup.number()
    .typeError('Points per euro must be a number')
    .required('Points per euro is required')
    .positive('Points per euro must be a positive number'),
  benefits: yup.string().optional(),
});

export const loginSchema = yup.object({
    email: yup.string().required('Email is required').email('Must be a valid email'),
    password: yup.string().required('Password is required'),
});
