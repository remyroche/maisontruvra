import { initializeAdminPage } from './admin_common.js';
import { ADMIN_API_BASE_URL } from './admin_config.js';
import { showToast } from './admin_ui.js';

function initCategoriesPage() {
    const token = localStorage.getItem('admin_token');
    const categoriesTableBody = document.querySelector('#categories-table tbody');
    const categoryForm = document.getElementById('category-form');
    const categoryIdInput = document.getElementById('category-id');
    const categoryNameInput = document.getElementById('category-name');

    const fetchCategories = async () => {
        try {
            const response = await fetch(`${ADMIN_API_BASE_URL}/categories`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Failed to fetch categories');
            const categories = await response.json();
            renderCategories(categories);
        } catch (error) {
            showToast(error.message, 'error');
        }
    };

    const renderCategories = (categories) => {
        categoriesTableBody.innerHTML = '';
        if (!categories || categories.length === 0) {
            categoriesTableBody.innerHTML = '<tr><td colspan="3">No categories found.</td></tr>';
            return;
        }
        categories.forEach(category => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${category.id}</td>
                <td>${category.name}</td>
                <td class="actions">
                    <button class="btn-edit" data-id="${category.id}" data-name="${category.name}">Edit</button>
                    <button class="btn-delete" data-id="${category.id}">Delete</button>
                </td>
            `;
            categoriesTableBody.appendChild(row);
        });
    };

    categoryForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const id = categoryIdInput.value;
        const name = categoryNameInput.value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${ADMIN_API_BASE_URL}/categories/${id}` : `${ADMIN_API_BASE_URL}/categories`;

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name })
            });
            if (!response.ok) throw new Error('Failed to save category');
            showToast('Category saved successfully.');
            categoryForm.reset();
            categoryIdInput.value = '';
            fetchCategories();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    categoriesTableBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-edit')) {
            const { id, name } = event.target.dataset;
            categoryIdInput.value = id;
            categoryNameInput.value = name;
            categoryNameInput.focus();
        }
        if (event.target.classList.contains('btn-delete')) {
            if (confirm('Are you sure? This might affect products in this category.')) {
                deleteCategory(event.target.dataset.id);
            }
        }
    });

    const deleteCategory = async (id) => {
        try {
            const response = await fetch(`${ADMIN_API_BASE_URL}/categories/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Failed to delete category');
            showToast('Category deleted.');
            fetchCategories();
        } catch (error) {
            showToast(error.message, 'error');
        }
    };

    fetchCategories();
}

initializeAdminPage(initCategoriesPage);
