<template>
  <div class="registration-form-container">
    <h2>Create Your Account</h2>
    <Form :validation-schema="schema" @submit="handleRegister" v-slot="{ isSubmitting }">
      <div class="form-group">
        <label for="firstName">First Name</label>
        <Field name="firstName" type="text" id="firstName" class="form-input" />
        <ErrorMessage name="firstName" class="error-message" />
      </div>

      <div class="form-group">
        <label for="lastName">Last Name</label>
        <Field name="lastName" type="text" id="lastName" class="form-input" />
        <ErrorMessage name="lastName" class="error-message" />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <Field name="email" type="email" id="email" class="form-input" />
        <ErrorMessage name="email" class="error-message" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <Field name="password" type="password" id="password" class="form-input" />
        <ErrorMessage name="password" class="error-message" />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <Field name="confirmPassword" type="password" id="confirmPassword" class="form-input" />
        <ErrorMessage name="confirmPassword" class="error-message" />
      </div>

      <button type="submit" class="submit-button" :disabled="isSubmitting">
        <span v-if="isSubmitting">Registering...</span>
        <span v-else>Create Account</span>
      </button>
    </Form>
  </div>
</template>

<script setup>
import { Form, Field, ErrorMessage } from 'vee-validate';
import { useAuthStore } from '@/stores/auth'; // Assuming you have an auth store
import { required, email, minLength, hasUppercase, hasLowercase, hasDigit, hasSpecialChar } from '@/validation/rules';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Define the validation schema using the imported rules
const schema = {
  firstName: (value) => required(value),
  lastName: (value) => required(value),
  email: (value) => required(value) && email(value),
  password: (value) => 
    required(value) && 
    minLength(value, [8]) && 
    hasUppercase(value) &&
    hasLowercase(value) &&
    hasDigit(value) &&
    hasSpecialChar(value),
  confirmPassword: (value, { form }) => {
    if (!value) return 'This field is required';
    return value === form.password ? true : 'Passwords must match';
  },
};

const handleRegister = async (values, { setErrors }) => {
  try {
    await authStore.register(values);
    // Redirect to login or a "check your email" page after successful registration
    router.push('/login'); 
  } catch (error) {
    // Assuming the API returns a 400 with an error message
    if (error.response && error.response.data.message) {
      setErrors({ email: error.response.data.message });
    } else {
      setErrors({ email: 'An unexpected error occurred. Please try again.' });
    }
  }
};
</script>

<style scoped>
/* Add some basic styling for the form */
.registration-form-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.25rem;
}
.error-message {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
.submit-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4a5568;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}
.submit-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}
</style>
