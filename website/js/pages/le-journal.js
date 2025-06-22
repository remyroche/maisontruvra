// website/source/js/pages/le-journal.js
document.addEventListener('DOMContentLoaded', () => {
    // This assumes a global API class is available
    const api = new API();
    const categoriesNav = document.getElementById('journal-categories-nav');
    const categoriesContainer = document.getElementById('categories-container');

    const renderCategories = (categories) => {
        if (!categoriesContainer) return;
        categoriesContainer.innerHTML = ''; // Clear existing
        categories.forEach(category => {
            const link = document.createElement('a');
            link.href = `?category=${category.slug}`;
            link.className = 'font-sans text-md text-brand-dark-gray hover:text-brand-burgundy transition-colors';
            link.textContent = category.name;
            link.dataset.slug = category.slug;
            categoriesContainer.appendChild(link);
        });
    };

    const fetchCategories = async () => {
        try {
            const categories = await api.get('/api/blog/categories');
            if (categories && categories.length > 0) {
                renderCategories(categories);
            }
        } catch (error) {
            console.error('Failed to load blog categories:', error);
            // Optionally hide the nav or show a message if categories fail to load
            if(categoriesNav) categoriesNav.style.display = 'none';
        }
    };
    
    // Add logic to filter articles when a category is clicked
    categoriesNav.addEventListener('click', (e) => {
        if (e.target.tagName === 'A') {
            e.preventDefault();
            
            // Remove active state from all links
            document.querySelectorAll('#journal-categories-nav a').forEach(link => {
                link.classList.remove('text-brand-burgundy', 'font-semibold', 'border-b-2', 'border-brand-burgundy');
                link.classList.add('text-brand-dark-gray');
            });
            
            // Add active state to clicked link
            e.target.classList.add('text-brand-burgundy', 'font-semibold', 'border-b-2', 'border-brand-burgundy');
            e.target.classList.remove('text-brand-dark-gray');

            const slug = e.target.dataset.slug;
            console.log(`Filtering by category: ${slug}`);
            // Future implementation: call a function to fetch and display articles for this slug
            // For now, it just visually updates the selected category.
        }
    });

    fetchCategories();
});
