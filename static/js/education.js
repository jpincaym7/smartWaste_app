document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.section-tab');
    const sections = document.querySelectorAll('.section-content');
    let currentSection = 0;

    // Gestor de tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            updateActiveTab(index);
        });
    });

    function updateActiveTab(index) {
        // Remover clases activas
        tabs.forEach(tab => tab.classList.remove('active'));
        sections.forEach(section => section.classList.remove('active'));

        // Activar tab y sección
        tabs[index].classList.add('active');
        sections[index].classList.add('active');
        
        // Scroll suave al contenido
        sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        currentSection = index;
    }

    // Soporte para gestos táctiles
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const SWIPE_THRESHOLD = 50;
        const diffX = touchStartX - touchEndX;

        if (Math.abs(diffX) > SWIPE_THRESHOLD) {
            if (diffX > 0 && currentSection < tabs.length - 1) {
                updateActiveTab(currentSection + 1);
            } else if (diffX < 0 && currentSection > 0) {
                updateActiveTab(currentSection - 1);
            }
        }
    }
});