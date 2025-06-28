<template>
  <div v-if="password.length > 0" class="mt-2 text-sm">
    <ul class="space-y-1">
      <li :class="getRuleClass(validations.length)">
        <span class="mr-2">{{ getIcon(validations.length) }}</span>
        At least 12 characters
      </li>
      <li :class="getRuleClass(validations.uppercase)">
        <span class="mr-2">{{ getIcon(validations.uppercase) }}</span>
        At least one uppercase letter (A-Z)
      </li>
      <li :class="getRuleClass(validations.lowercase)">
        <span class="mr-2">{{ getIcon(validations.lowercase) }}</span>
        At least one lowercase letter (a-z)
      </li>
      <li :class="getRuleClass(validations.number)">
        <span class="mr-2">{{ getIcon(validations.number) }}</span>
        At least one number (0-9)
      </li>
      <li :class="getRuleClass(validations.special)">
        <span class="mr-2">{{ getIcon(validations.special) }}</span>
        At least one special character (!@#$%^&*)
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  password: {
    type: String,
    required: true,
    default: '',
  },
});

const validations = computed(() => {
  const p = props.password;
  return {
    length: p.length >= 12,
    uppercase: /[A-Z]/.test(p),
    lowercase: /[a-z]/.test(p),
    number: /[0-9]/.test(p),
    special: /[!@#$%^&*]/.test(p),
  };
});

const getRuleClass = (isValid) => {
  return isValid
    ? 'text-green-600 flex items-center transition-colors duration-300'
    : 'text-gray-500 flex items-center transition-colors duration-300';
};

const getIcon = (isValid) => {
  return isValid ? '✓' : '•';
};
</script>