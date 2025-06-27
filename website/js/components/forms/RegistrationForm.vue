<template>
    <div class="registration-form">
        <h3 class="text-xl font-semibold mb-4 text-center">Create Your Account</h3>
        <Form @submit="handleRegister" :validation-schema="registrationSchema" v-slot="{ errors }">
            <div class="space-y-4">
                <div>
                    <label for="first_name">First Name</label>
                    <Field name="first_name" type="text" id="first_name" placeholder="John"
                           :class="{'border-red-500': errors.first_name, 'border-gray-300': !errors.first_name}" />
                    <ErrorMessage name="first_name" class="error-message" />
                </div>
                <div>
                    <label for="last_name">Last Name</label>
                    <Field name="last_name" type="text" id="last_name" placeholder="Doe"
                           :class="{'border-red-500': errors.last_name, 'border-gray-300': !errors.last_name}" />
                    <ErrorMessage name="last_name" class="error-message" />
                </div>
                <div>
                    <label for="email">Email</label>
                    <Field name="email" type="email" id="email" placeholder="john.doe@example.com"
                           :class="{'border-red-500': errors.email, 'border-gray-300': !errors.email}" />
                    <ErrorMessage name="email" class="error-message" />
                </div>
                <div>
                    <label for="password">Password</label>
                    <Field name="password" type="password" id="password"
                           :class="{'border-red-500': errors.password, 'border-gray-300': !errors.password}" />
                    <ErrorMessage name="password" class="error-message" />
                </div>
                 <div>
                    <label for="confirm_password">Confirm Password</label>
                    <Field name="confirm_password" type="password" id="confirm_password"
                           :class="{'border-red-500': errors.confirm_password, 'border-gray-300': !errors.confirm_password}" />
                    <ErrorMessage name="confirm_password" class="error-message" />
                </div>
                <div class="flex items-center">
                    <Field name="agree_to_terms" type="checkbox" id="agree_to_terms" :value="true"
                           class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
                    <label for="agree_to_terms" class="ml-2 block text-sm text-gray-900">
                        I agree to the <a href="/terms" class="text-indigo-600 hover:underline">Terms and Conditions</a>
                    </label>
                </div>
                 <ErrorMessage name="agree_to_terms" class="error-message" />
            </div>

            <button type="submit" class="w-full btn-primary mt-6">
                Register
            </button>
        </Form>
    </div>
</template>

<script setup>
import { Form, Field, ErrorMessage } from 'vee-validate';
import { registrationSchema } from '../../validation/schemas';
import { useAuthStore } from '../../stores/auth';
import { useNotificationStore } from '../../stores/notification';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

async function handleRegister(values) {
    const { first_name, last_name, email, password } = values;
    const success = await authStore.register({ first_name, last_name, email, password });
    if (success) {
        notificationStore.showNotification({ message: 'Registration successful! Please check your email to verify your account.', type: 'success' });
    } else {
        notificationStore.showNotification({ message: authStore.error || 'Registration failed.', type: 'error' });
    }
}
</script>

<style scoped>
/* Basic form styling */
label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}
input, .btn-primary {
    width: 100%;
    padding: 0.75rem;
    border-radius: 0.375rem;
    border: 1px solid;
}
.error-message {
    color: #ef4444; /* red-500 */
    font-size: 0.875rem; /* text-sm */
    margin-top: 0.25rem;
}
.btn-primary {
    background-color: #4f46e5; /* indigo-600 */
    color: white;
    border-color: transparent;
    cursor: pointer;
}
.btn-primary:hover {
    background-color: #4338ca; /* indigo-700 */
}
</style>
