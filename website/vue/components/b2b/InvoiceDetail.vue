<template>
  <div class="p-6">
    <div v-if="isLoading">Chargement de la facture...</div>
    <div v-else-if="invoice">
      <h2 class="text-3xl font-serif text-truffle-burgundy mb-6">Détails de la Facture #{{ invoice.id }}</h2>

      <div class="invoice-container bg-white p-8 rounded-lg shadow-lg mb-8" v-html="invoiceHtml">
          </div>

      <div v-if="invoice.status === 'pending_signature'" class="mt-8">
        <h3 class="text-xl font-semibold mb-3">Signer la Facture</h3>
        <p class="text-sm text-gray-600 mb-4">Veuillez signer dans le champ ci-dessous pour accepter les termes de cette facture.</p>
        <div class="border border-gray-400 rounded-md">
            <canvas ref="signaturePadCanvas" class="w-full h-48"></canvas>
        </div>
        <div class="mt-4 space-x-4">
            <button @click="clearSignature" class="btn-secondary py-2 px-4 rounded-md">Effacer</button>
            <button @click="saveSignature" class="btn-primary py-2 px-6 rounded-md">Signer et Accepter</button>
        </div>
      </div>
      
      <div v-if="invoice.status === 'signed'">
          <h3 class="text-xl font-semibold text-green-700">Facture Signée</h3>
          <p class="text-gray-700">Merci. Votre facture est maintenant en attente de paiement. Vous serez contacté par notre équipe pour finaliser la transaction.</p>
          <img :src="invoice.signature_data" alt="Your Signature" class="mt-4 border rounded-md p-2 bg-gray-100" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../js/api-client';
import SignaturePad from 'signature_pad';

const route = useRoute();
const invoice = ref(null);
const isLoading = ref(true);
const signaturePadCanvas = ref(null);
let signaturePad = null;

const invoiceHtml = computed(() => {
    // In a real application, you would fetch an HTML template and populate it with invoice data.
    // For this example, we will generate simple HTML.
    if (!invoice.value) return '';
    
    let itemsHtml = invoice.value.items.map(item => `
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">${item.description}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">${item.quantity}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.unit_price.toFixed(2)} €</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.total_price.toFixed(2)} €</td>
        </tr>
    `).join('');

    return `
        <h1 style="font-size: 24px; color: #5a2d2d;">Facture</h1>
        <p><strong>Facture N°:</strong> ${invoice.value.id}</p>
        <p><strong>Date:</strong> ${new Date(invoice.value.created_at).toLocaleDateString('fr-FR')}</p>
        <hr style="margin: 20px 0;" />
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="text-align: left; padding: 8px; border-bottom: 2px solid #333;">Description</th>
                    <th style="text-align: center; padding: 8px; border-bottom: 2px solid #333;">Quantité</th>
                    <th style="text-align: right; padding: 8px; border-bottom: 2px solid #333;">Prix Unitaire</th>
                    <th style="text-align: right; padding: 8px; border-bottom: 2px solid #333;">Total</th>
                </tr>
            </thead>
            <tbody>${itemsHtml}</tbody>
            <tfoot>
                <tr>
                    <td colspan="3" style="text-align: right; padding: 10px; font-weight: bold;">Total HT</td>
                    <td style="text-align: right; padding: 10px; font-weight: bold;">${invoice.value.total_amount.toFixed(2)} €</td>
                </tr>
            </tfoot>
        </table>
    `;
});


async function fetchInvoice() {
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/api/b2b/invoices/${route.params.id}`);
    invoice.value = response.data;
  } catch (error) {
    console.error("Failed to fetch invoice:", error);
  } finally {
    isLoading.value = false;
    if (invoice.value?.status === 'pending_signature') {
      // nextTick ensures canvas is rendered before initializing
      import('vue').then(vue => vue.nextTick(initSignaturePad));
    }
  }
}

function initSignaturePad() {
  if (signaturePadCanvas.value) {
    signaturePad = new SignaturePad(signaturePadCanvas.value);
  }
}

function clearSignature() {
  if (signaturePad) {
    signaturePad.clear();
  }
}

async function saveSignature() {
  if (signaturePad && !signaturePad.isEmpty()) {
    const signatureDataURL = signaturePad.toDataURL(); // PNG format
    try {
      await apiClient.post(`/api/b2b/invoices/${invoice.value.id}/sign`, {
        signature_data: signatureDataURL
      });
      // Refresh invoice data to show new status
      await fetchInvoice();
    } catch (error) {
      console.error("Failed to save signature:", error);
      // TODO: Show notification
    }
  } else {
    alert("Veuillez d'abord signer.");
  }
}

onMounted(fetchInvoice);
</script>
