document.addEventListener('click', function(e) {
    const prevBtn = e.target.closest('.carousel-btn.prev');
    const nextBtn = e.target.closest('.carousel-btn.next');

    if (!prevBtn && !nextBtn) return;

    const wrapper = e.target.closest('.carousel-wrapper');
    if (!wrapper) return;

    const carousel = wrapper.querySelector('.event-carousel');
    if (!carousel) return;

    const scrollAmount = () => {
        const card = carousel.querySelector('.event-card');
        if (!card) return 300; // Fallback
        const style = window.getComputedStyle(card);
        const gap = parseInt(style.marginRight || 0);
        return card.offsetWidth + gap + 22;
    };

    if (prevBtn) {
        carousel.scrollBy({
            left: -scrollAmount(),
            behavior: 'smooth'
        });
    }

    if (nextBtn) {
        carousel.scrollBy({
            left: scrollAmount(),
            behavior: 'smooth'
        });
    }
});
