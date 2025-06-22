// website/source/admin/js/admin_manage_articles.js

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const addNewArticleBtn = document.getElementById('add-new-article-btn');
    const editorContainer = document.getElementById('article-editor-container');
    const form = document.getElementById('article-form');
    const formTitle = document.getElementById('article-form-title');
    const cancelBtn = document.getElementById('cancel-article-edit-btn');
    const tableBody = document.getElementById('articles-table-body');

    const articleIdInput = document.getElementById('article-id');
    const titleInput = document.getElementById('article-title');
    const categorySelect = document.getElementById('article-category');
    const statusSelect = document.getElementById('article-status');
    const contentTypeSelect = document.getElementById('article-content-type');
    const contentTextarea = document.getElementById('article-content');
    const htmlWarning = document.getElementById('html-warning');
    
    // --- State ---
    const api = new AdminAPI();
    let easyMDE = null; // To hold the EasyMDE instance
    let articlesCache = [];

    // --- Editor Logic ---
    const initializeMarkdownEditor = () => {
        if (!easyMDE) {
            easyMDE = new EasyMDE({
                element: contentTextarea,
                spellChecker: false,
                status: ["lines", "words"],
                toolbar: ["bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "|", "preview", "side-by-side", "fullscreen"],
            });
        }
        htmlWarning.classList.add('hidden');
    };

    const destroyMarkdownEditor = () => {
        if (easyMDE) {
            easyMDE.toTextArea();
            easyMDE = null;
        }
        htmlWarning.classList.remove('hidden');
    };
    
    const setupEditorForContentType = (type) => {
        if (type === 'markdown') {
            initializeMarkdownEditor();
        } else {
            destroyMarkdownEditor();
        }
    };

    // --- UI Logic ---
    const showEditor = (mode = 'create', article = null) => {
        form.reset();
        articleIdInput.value = '';
        
        if (mode === 'create') {
            formTitle.textContent = 'Create New Article';
            setupEditorForContentType('markdown'); // Default to markdown
        } else if (mode === 'edit' && article) {
            formTitle.textContent = `Edit Article: ${article.title}`;
            articleIdInput.value = article.id;
            titleInput.value = article.title;
            categorySelect.value = article.category?.id || '';
            statusSelect.value = article.status;
            contentTypeSelect.value = article.content_type;
            
            setupEditorForContentType(article.content_type);
            
            if (article.content_type === 'markdown' && easyMDE) {
                easyMDE.value(article.content);
            } else {
                contentTextarea.value = article.content;
            }
        }
        editorContainer.classList.remove('hidden');
        editorContainer.scrollIntoView({ behavior: 'smooth' });
    };

    const hideEditor = () => {
        editorContainer.classList.add('hidden');
        resetFormState();
    };

    const resetFormState = () => {
        form.reset();
        articleIdInput.value = '';
        if (easyMDE) {
            easyMDE.value('');
        }
    };

    // --- Data Rendering ---
    const renderArticlesTable = (articles) => {
        tableBody.innerHTML = '';
        if (articles.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-500">No articles created yet.</td></tr>';
            return;
        }
        articles.forEach(article => {
            const pubDate = article.publication_date ? new Date(article.publication_date).toLocaleDateString() : 'N/A';
            const row = tableBody.insertRow();
            row.innerHTML = `
                <td class="py-3 px-2 font-semibold text-brand-dark-brown">${article.title}</td>
                <td class="py-3 px-2">${article.category?.name || 'Uncategorized'}</td>
                <td class="py-3 px-2">${article.status === 'published' ? '<span class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">Published</span>' : '<span class="bg-amber-100 text-amber-800 text-xs font-medium px-2.5 py-0.5 rounded-full">Draft</span>'}</td>
                <td class="py-3 px-2">${pubDate}</td>
                <td class="py-3 px-2 text-right">
                    <button class="edit-btn font-sans font-semibold text-blue-600 hover:underline" data-id="${article.id}">Edit</button>
                    <button class="delete-btn font-sans font-semibold text-red-600 hover:underline ml-4" data-id="${article.id}">Delete</button>
                </td>
            `;
        });
    };

    // --- API Calls & Data Fetching ---
    const loadInitialData = async () => {
        try {
            const [articles, categories] = await Promise.all([
                api.get('/admin/api/blog/articles'),
                api.get('/admin/api/blog/categories')
            ]);
            
            articlesCache = articles;
            renderArticlesTable(articles);

            categorySelect.innerHTML = '<option value="">Select a category...</option>';
            categories.forEach(cat => {
                if (cat.is_active) {
                    const option = document.createElement('option');
                    option.value = cat.id;
                    option.textContent = cat.name;
                    categorySelect.appendChild(option);
                }
            });

        } catch (error) {
            console.error('Failed to load initial data:', error);
            alert('Error: Could not load data for the article editor.');
        }
    };

    // --- Event Listeners ---
    addNewArticleBtn.addEventListener('click', () => showEditor('create'));
    cancelBtn.addEventListener('click', hideEditor);
    
    contentTypeSelect.addEventListener('change', (e) => {
        setupEditorForContentType(e.target.value);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = articleIdInput.value;
        const content = easyMDE ? easyMDE.value() : contentTextarea.value;

        const payload = {
            title: titleInput.value.trim(),
            category_id: categorySelect.value,
            status: statusSelect.value,
            content_type: contentTypeSelect.value,
            content: content
        };

        if (!payload.title || !payload.category_id) {
            alert('Title and Category are required.');
            return;
        }

        try {
            if (id) {
                await api.put(`/admin/api/blog/articles/${id}`, payload);
            } else {
                await api.post('/admin/api/blog/articles', payload);
            }
            hideEditor();
            await loadInitialData(); // Refresh table
        } catch (error) {
            const errorData = await error.response.json().catch(() => ({ error: 'Could not save article.' }));
            alert(`Error: ${errorData.error}`);
        }
    });
    
    tableBody.addEventListener('click', async (e) => {
        const target = e.target;
        if (target.classList.contains('edit-btn')) {
            const id = parseInt(target.dataset.id, 10);
            try {
                const articleToEdit = await api.get(`/admin/api/blog/articles/${id}`);
                showEditor('edit', articleToEdit);
            } catch (error) {
                alert('Could not fetch article details for editing.');
            }
        } else if (target.classList.contains('delete-btn')) {
            const id = parseInt(target.dataset.id, 10);
            if (confirm('Are you sure you want to delete this article?')) {
                try {
                    await api.delete(`/admin/api/blog/articles/${id}`);
                    await loadInitialData(); // Refresh table
                } catch (error) {
                    alert('Error: Could not delete the article.');
                }
            }
        }
    });

    // --- Initial Load ---
    loadInitialData();
});
