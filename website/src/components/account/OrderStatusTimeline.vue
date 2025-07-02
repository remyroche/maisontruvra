<!-- website/src/components/account/OrderStatusTimeline.vue -->
<template>
  <div>
    <h2 class="sr-only">Order Status</h2>
    <div class="p-4 rounded-lg bg-gray-50">
      <nav aria-label="Progress">
        <ol role="list" class="flex items-center">
          <li v-for="(step, stepIdx) in steps" :key="step.name" class="relative" :class="{'flex-1': stepIdx !== steps.length - 1}">
            <template v-if="step.status === 'complete'">
              <div class="absolute inset-0 flex items-center" aria-hidden="true" v-if="stepIdx !== steps.length - 1">
                <!-- Completed line -->
                <div class="h-0.5 w-full bg-brand-gold" />
              </div>
              <div class="relative flex h-8 w-8 items-center justify-center rounded-full bg-brand-gold">
                <CheckIcon class="h-5 w-5 text-white" aria-hidden="true" />
              </div>
              <span class="absolute -bottom-6 w-max text-xs text-brand-charcoal">{{ step.name }}</span>
            </template>
            <template v-else-if="step.status === 'current'">
              <div class="absolute inset-0 flex items-center" aria-hidden="true" v-if="stepIdx !== steps.length - 1">
                <!-- Upcoming line -->
                <div class="h-0.5 w-full bg-gray-200" />
              </div>
              <div class="relative flex h-8 w-8 items-center justify-center rounded-full border-2 border-brand-gold bg-white animate-pulse">
                <span class="h-2.5 w-2.5 rounded-full bg-brand-gold" aria-hidden="true" />
              </div>
              <span class="absolute -bottom-6 w-max text-xs font-semibold text-brand-burgundy">{{ step.name }}</span>
            </template>
            <template v-else>
              <div class="absolute inset-0 flex items-center" aria-hidden="true" v-if="stepIdx !== steps.length - 1">
                <!-- Upcoming line -->
                <div class="h-0.5 w-full bg-gray-200" />
              </div>
              <div class="relative flex h-8 w-8 items-center justify-center rounded-full border-2 border-gray-300 bg-white">
                 <span class="h-2.5 w-2.5 rounded-full bg-transparent" aria-hidden="true" />
              </div>
              <span class="absolute -bottom-6 w-max text-xs text-gray-500">{{ step.name }}</span>
            </template>
          </li>
        </ol>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue';
import { CheckIcon } from '@heroicons/vue/24/solid';

const props = defineProps({
  status: {
    type: String,
    required: true,
    // Maps to the OrderStatusEnum values from the backend
    validator: (value) => ['Confirmed', 'Packing', 'Shipped', 'Delivered', 'Cancelled'].includes(value),
  },
});

const stepOrder = ['Confirmed', 'Packing', 'Shipped', 'Delivered'];

const steps = computed(() => {
  const currentStepIndex = stepOrder.indexOf(props.status);

  // If the order is cancelled, show all steps as neutral but indicate cancellation
  if (props.status === 'Cancelled') {
      return stepOrder.map(name => ({ name, status: 'upcoming' }));
  }

  return stepOrder.map((name, index) => {
    let status = 'upcoming';
    if (index < currentStepIndex) {
      status = 'complete';
    } else if (index === currentStepIndex) {
      status = 'current';
    }
    return { name, status };
  });
});
</script>
