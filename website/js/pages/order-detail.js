// website/source/js/pages/order-detail.js (New File)
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('order-detail-container');
    const params = new URLSearchParams(window.location.search);
    const orderId = params.get('id');

    if (!orderId) {
        container.innerHTML = `<p class="text-center text-red-500">No order ID specified.</p>`;
        return;
    }

    try {
        const response = await apiClient.get(`/orders/${orderId}`);
        if (!response.ok) {
            throw new Error(response.data.msg || 'Failed to fetch order details');
        }
        renderOrderDetails(response.data);
    } catch (error) {
        container.innerHTML = `<p class="text-center text-red-500">${error.message}</p>`;
    }
});

function renderOrderDetails(order) {
    const container = document.getElementById('order-detail-container');
    
    let itemsHtml = '';
    order.items.forEach(item => {
        itemsHtml += `
            <li class="flex py-6">
                <div class="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
                    <img src="${item.product.image_url || '[https://placehold.co/200x200](https://placehold.co/200x200)'}" alt="${item.product.name}" class="h-full w-full object-cover object-center">
                </div>
                <div class="ml-4 flex flex-1 flex-col">
                    <div>
                        <div class="flex justify-between text-base font-medium text-gray-900">
                            <h3>${item.product.name}</h3>
                            <p class="ml-4">$${(item.price * item.quantity).toFixed(2)}</p>
                        </div>
                    </div>
                    <div class="flex flex-1 items-end justify-between text-sm">
                        <p class="text-gray-500">Qty ${item.quantity}</p>
                    </div>
                </div>
            </li>
        `;
    });

    let historyHtml = '';
    order.history.forEach(entry => {
        historyHtml += `
            <div class="relative pb-8">
                <span class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true"></span>
                <div class="relative flex space-x-3">
                    <div>
                        <span class="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                            <!-- Heroicon name: solid/check -->
                            <svg class="h-5 w-5 text-white" xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
                        </span>
                    </div>
                    <div class="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                            <p class="text-sm text-gray-500">${entry.status}</p>
                            <p class="text-xs text-gray-400">${entry.notes || ''}</p>
                        </div>
                        <div class="text-right text-sm whitespace-nowrap text-gray-500">
                           <time datetime="${entry.timestamp}">${new Date(entry.timestamp).toLocaleString()}</time>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="bg-white shadow sm:rounded-lg">
            <div class="px-4 py-5 sm:px-6">
                <h2 class="text-2xl font-extrabold tracking-tight text-gray-900">Order #${order.id}</h2>
                <p class="mt-1 max-w-2xl text-sm text-gray-500">Status: <span class="font-medium text-indigo-600">${order.status}</span></p>
            </div>
            <div class="border-t border-gray-200">
                <ul role="list" class="divide-y divide-gray-200">${itemsHtml}</ul>
            </div>
             <div class="border-t border-gray-200 px-4 py-6 sm:px-6">
                <h3 class="text-lg font-medium text-gray-900">Order History</h3>
                <div class="mt-6 flow-root">
                   ${historyHtml}
                </div>
            </div>
        </div>
    `;
}
