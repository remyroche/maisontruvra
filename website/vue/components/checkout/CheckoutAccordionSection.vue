<template>
  <div class="border border-gray-200 rounded-lg">
    <div 
      @click="$emit('activate')" 
      class="flex items-center justify-between p-4 cursor-pointer"
      :class="{'bg-gray-50': !isComplete, 'hover:bg-gray-100': !isComplete}"
    >
      <div class="flex items-center">
        <div 
          class="flex items-center justify-center w-8 h-8 rounded-full"
          :class="{
            'bg-primary text-white': isActive, 
            'bg-green-500 text-white': isComplete && !isActive,
            'bg-gray-200 text-gray-600': !isActive && !isComplete
          }"
        >
          <svg v-if="isComplete && !isActive" class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.052-.143z" clip-rule="evenodd" />
          </svg>
          <span v-else>{{ stepNumber }}</span>
        </div>
        <h3 class="ml-4 text-lg font-medium" :class="{'text-primary': isActive, 'text-gray-900': !isActive}">
          {{ title }}
        </h3>
      </div>
      <div v-if="isComplete && !isActive" class="text-sm">
        <button @click.stop="$emit('activate')" class="font-medium text-primary hover:text-indigo-700">Edit</button>
      </div>
    </div>

    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform opacity-0 -translate-y-4"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 -translate-y-4"
    >
      <div v-if="isActive" class="p-6 border-t border-gray-200">
        <!-- Summary slot for completed section view -->
        <div v-if="isComplete" class="mb-4">
            <slot name="summary"></slot>
        </div>
        <!-- Main content for the active section -->
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup>
defineProps({
  stepNumber: Number,
  title: String,
  isActive: Boolean,
  isComplete: Boolean,
});

defineEmits(['activate']);
</script>
