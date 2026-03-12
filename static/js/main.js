// NewsHub main.js

// Auto slug generation
function initSlugGenerator() {
    const titleField = document.getElementById('id_title');
    const slugField = document.getElementById('id_slug');
    if (titleField && slugField) {
        titleField.addEventListener('input', function() {
            if (!slugField.dataset.modified) {
                slugField.value = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .replace(/^-+|-+$/g, '');
            }
        });
        slugField.addEventListener('input', function() {
            this.dataset.modified = 'true';
        });
    }
}

document.addEventListener('DOMContentLoaded', initSlugGenerator);
