<template>
  <form @submit.prevent="submitForm" class="space-y-4">
    <div>
      <label for="name" class="block text-sm font-medium text-gray-700">Product Name</label>
      <input type="text" id="name" v-model="form.name" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
    </div>

    <div>
      <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
      <textarea id="description" v-model="form.description" rows="4" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"></textarea>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
            <label for="price" class="block text-sm font-medium text-gray-700">Price</label>
            <input type="number" step="0.01" id="price" v-model.number="form.price" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
        </div>
        <div>
            <label for="sku" class="block text-sm font-medium text-gray-700">SKU</label>
            <input type="text" id="sku" v-model="form.sku" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
            <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
            <select id="category" v-model="form.category_id" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
                <option :value="null">None</option>
                <option v-for="cat in productsStore.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
        </div>
        <div>
            <label for="collection" class="block text-sm font-medium text-gray-700">Collection</label>
            <select id="collection" v-model="form.collection_id" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
                 <option :value="null">None</option>
                <option v-for="col in productsStore.collections" :key="col.id" :value="col.id">{{ col.name }}</option>
            </select>
        </div>
    </div>
    
    <div>
        <label class="block text-sm font-medium text-gray-700">Images</label>
        <input type="file" multiple @change="handleImageUpload" class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100">
        <div class="mt-2 flex space-x-2">
            <div v-for="(image, index) in imagePreviews" :key="index" class="relative">
                <img :src="image" class="h-20 w-20 object-cover rounded">
            </div>
        </div>
    </div>

    <div class="flex items-center">
      <input id="is_published" type="checkbox" v-model="form.is_published" class="h-4 w-4 text-indigo-600 rounded">
      <label for="is_published" class="ml-2 block text-sm text-gray-900">Published</label>
    </div>

    <div class="flex justify-end space-x-4">
        <button type="button" @click="$emit('cancel')" class="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300">Cancel</button>
        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">Save Product</button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAdminProductsStore } from '@/js/stores/adminProducts';

const props = defineProps({
  product: {
    type: Object,
    default: () => ({ name: '', description: '', price: 0, sku: '', category_id: null, collection_id: null, is_published: true, images: [] })
  }
});
const emit = defineEmits(['save', 'cancel']);
const productsStore = useAdminProductsStore();

const form = ref({ ...props.product });
const imageFiles = ref([]);
const imagePreviews = ref([]);

watch(() => props.product, (newProduct) => {
  form.value = { ...newProduct };
  imagePreviews.value = newProduct.images ? newProduct.images.map(img => img.url) : [];
}, { immediate: true, deep: true });

onMounted(() => {
    productsStore.fetchFormData();
});

const handleImageUpload = (event) => {
    const files = Array.from(event.target.files);
    imageFiles.value = files;
    imagePreviews.value = files.map(file => URL.createObjectURL(file));
};

const submitForm = () => {
    const dataToSend = { ...form.value };
    if (imageFiles.value.length > 0) {
        dataToSend.images = imageFiles.value;
    } else {
        delete dataToSend.images; // Don't send empty image array
    }
    emit('save', dataToSend);
};
</script>

