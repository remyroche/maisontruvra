// website/source/admin/js/admin_products.js (New File)
document.addEventListener('DOMContentLoaded', () => {
    const productColumns = [
        { header: 'ID', key: 'id' },
        { header: 'Name', key: 'name', cell: p => `<div class="font-medium text-gray-900">${p.name}</div>` },
        { header: 'Price', key: 'price', cell: p => `$${parseFloat(p.price).toFixed(2)}` },
        { header: 'SKU', key: 'sku'},
        { header: 'Stock', key: 'stock_level', cell: p => p.stock_level > 0 ? `${p.stock_level}` : `<span class="text-red-600">Out of Stock</span>` },
        { header: 'Actions', key: 'id', cell: p => `<button class="text-indigo-600 hover:text-indigo-900" onclick="editProduct(${p.id})">Edit</button>` }
    ];
    
    const fetchProducts = async (page = 1) => {
        const response = await apiClient.get(`/admin/products?page=${page}&per_page=15`);
        if (!response.ok) throw new Error('Failed to fetch products');
        return response.data;
    };

    new DataTableFactory('products-table-container', {
        columns: productColumns,
        fetchData: fetchProducts,
        dataKey: 'products',
        totalKey: 'total_products'
    });
});

function editProduct(productId) {
    alert(`Editing product with ID: ${productId}`);
}
