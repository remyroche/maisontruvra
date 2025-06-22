// website/source/admin/js/admin_manage_blog_categories.js
document.addEventListener('DOMContentLoaded', () => {
    // This assumes a global AdminAPI class is available for making authenticated requests
    const api = new AdminAPI(); 
    const form = document.getElementById('category-form');
    const formTitle = document.getElementById('category-form-title');
    const categoryIdInput = document.getElementById('category-id');
    const categoryNameInput = document.getElementById('category-name');
    const categoryDescriptionInput = document.getElementById('category-description');
    const categoryIsActiveInput = document.getElementById('category-is-active');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const tableBody = document.getElementById('categories-table-body');

    let categoriesCache = [];

    const resetForm = () => {
        form.reset();
        categoryIdInput.value = '';
        formTitle.textContent = 'Add New Category';
        cancelEditBtn.classList.add('hidden');
    };

    const renderTable = (categories) => {
        tableBody.innerHTML = '';
        if (categories.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-gray-500">No categories created yet.</td></tr>';
            return;
        }
        categories.forEach(category => {
            const row = tableBody.insertRow();
            row.className = 'border-b border-brand-light-gray';
            row.innerHTML = `
                <td class="py-3 px-2 font-semibold text-brand-dark-brown">${category.name}</td>
                <td class="py-3 px-2 text-brand-dark-gray">${category.description || '—'}</td>
                <td class="py-3 px-2">${category.is_active ? '<span class="bg-green-100 text-green-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full">Active</span>' : '<span class="bg-red-100 text-red-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full">Inactive</span>'}</td>
                <td class="py-3 px-2 text-right">
                    <button class="edit-btn font-sans font-semibold text-blue-600 hover:underline" data-id="${category.id}">Edit</button>
                    <button class="delete-btn font-sans font-semibold text-red-600 hover:underline ml-4" data-id="${category.id}">Delete</button>
                </td>
            `;
        });
    };

    const fetchCategories = async () => {
        try {
            categoriesCache = await api.get('/admin/api/blog/categories');
            renderTable(categoriesCache);
        } catch (error) {
            console.error('Failed to fetch categories:', error);
            alert('Error: Could not load categories.');
        }
    };

    const populateFormForEdit = (id) => {
        const category = categoriesCache.find(c => c.id === id);
        if (category) {
            formTitle.textContent = `Edit Category: ${category.name}`;
            categoryIdInput.value = category.id;
            categoryNameInput.value = category.name;
            categoryDescriptionInput.value = category.description;
            categoryIsActiveInput.checked = category.is_active;
            cancelEditBtn.classList.remove('hidden');
            form.scrollIntoView({ behavior: 'smooth' });
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = categoryIdInput.value;
        const payload = {
            name: categoryNameInput.value.trim(),
            description: categoryDescriptionInput.value.trim(),
            is_active: categoryIsActiveInput.checked
        };

        if (!payload.name) {
            alert('Category name is required.');
            return;
        }

        try {
            if (id) {
                await api.put(`/admin/api/blog/categories/${id}`, payload);
            } else {
                await api.post('/admin/api/blog/categories', payload);
            }
            resetForm();
            await fetchCategories();
        } catch (error) {
            const errorData = await error.response.json().catch(() => ({ error: 'Could not save category.' }));
            alert(`Error: ${errorData.error}`);
            console.error('Failed to save category:', error);
        }
    });

    tableBody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const id = parseInt(e.target.dataset.id, 10);
            populateFormForEdit(id);
        } else if (e.target.classList.contains('delete-btn')) {
            const id = parseInt(e.target.dataset.id, 10);
            if (confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
                try {
                    await api.delete(`/admin/api/blog/categories/${id}`);
                    await fetchCategories();
                } catch (error) {
                    alert('Error: Could not delete category.');
                    console.error('Failed to delete category:', error);
                }
            }
        }
    });

    cancelEditBtn.addEventListener('click', resetForm);
    fetchCategories(); // Initial load
});
