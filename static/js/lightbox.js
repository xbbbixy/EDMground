
(function() {
    // Prevent re-initialization on SPA-like navigation
    if (window.lightboxInitialized) {
        return;
    }
    window.lightboxInitialized = true;

    // 1. Create and inject lightbox HTML into the body
    const lightboxContainer = document.createElement('div');
    lightboxContainer.id = 'image-lightbox';
    lightboxContainer.className = 'lightbox';
    lightboxContainer.innerHTML = `
        <span class="lightbox-close">&times;</span>
        <img class="lightbox-content">
    `;
    document.body.appendChild(lightboxContainer);

    const lightboxImage = lightboxContainer.querySelector('.lightbox-content');
    const closeButton = lightboxContainer.querySelector('.lightbox-close');

    // 2. Define a function to close the lightbox
    const closeLightbox = () => {
        lightboxContainer.style.display = 'none';
    };

    // 3. Attach event listeners for closing actions
    closeButton.addEventListener('click', closeLightbox);
    lightboxContainer.addEventListener('click', (e) => {
        // Close if the dark backdrop area is clicked, but not the image itself
        if (e.target === lightboxContainer) {
            closeLightbox();
        }
    });
    document.addEventListener('keydown', (e) => {
        // Close on 'Escape' key press
        if (e.key === 'Escape') {
            closeLightbox();
        }
    });

    // 4. Use event delegation to listen for clicks on trigger images
    document.body.addEventListener('click', (e) => {
        if (e.target.matches('img.lightbox-trigger')) {
            // If the clicked image is inside a link, prevent the link from opening
            e.preventDefault();
            
            // Set the image source and display the lightbox
            lightboxImage.src = e.target.src;
            lightboxContainer.style.display = 'flex';
        }
    });
})();
