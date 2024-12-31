document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));

    // Parallax effect on scroll
    let lastScrollY = window.scrollY;
    const parallaxSections = document.querySelectorAll('.parallax-section');

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        const delta = (scrollY - lastScrollY) * 0.3;

        parallaxSections.forEach((section) => {
            const transform = parseFloat(section.style.transform.replace(/[^\d.-]/g, '') || 0);
            section.style.transform = `translateY(${transform + delta}px)`;
        });

        lastScrollY = scrollY;
    }, { passive: true });

    // Swipe handling for category cards
    const categoryContainer = document.querySelector('.swipe-container');
    let startX;
    let scrollLeft;

    categoryContainer.addEventListener('touchstart', (e) => {
        startX = e.touches[0].pageX - categoryContainer.offsetLeft;
        scrollLeft = categoryContainer.scrollLeft;
    }, { passive: true });

    categoryContainer.addEventListener('touchmove', (e) => {
        if (!startX) return;
        const x = e.touches[0].pageX - categoryContainer.offsetLeft;
        const walk = (x - startX) * 2;
        categoryContainer.scrollLeft = scrollLeft - walk;
    }, { passive: true });
});

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('instructionModal');
    const modalContent = modal.querySelector('.p-6');
    const dragHandle = modal.querySelector('.modal-drag-handle');
    const backdrop = document.getElementById('modalBackdrop');
    
    let startY = 0;
    let currentY = 0;
    let initialModalHeight = 0;
    let isDragging = false;
    let lastTapTime = 0;
    const DOUBLE_TAP_DELAY = 300;
    const VELOCITY_THRESHOLD = 0.5;
    const MIN_DRAG_THRESHOLD = 10;

    // Modal states
    const MODAL_STATES = {
        FULL: 'full',
        PARTIAL: 'partial',
        CLOSED: 'closed'
    };
    let currentState = MODAL_STATES.PARTIAL;

    // Touch handling utilities
    let velocityTracking = {
        positions: [],
        timestamps: [],
        maxTrackingPoints: 5
    };

    function calculateVelocity() {
        if (velocityTracking.positions.length < 2) return 0;
        
        const positions = velocityTracking.positions;
        const timestamps = velocityTracking.timestamps;
        const lastIndex = positions.length - 1;
        
        const deltaY = positions[lastIndex] - positions[0];
        const deltaTime = (timestamps[lastIndex] - timestamps[0]) / 1000;
        
        return deltaY / deltaTime;
    }

    function trackVelocity(y, timestamp) {
        velocityTracking.positions.push(y);
        velocityTracking.timestamps.push(timestamp);

        if (velocityTracking.positions.length > velocityTracking.maxTrackingPoints) {
            velocityTracking.positions.shift();
            velocityTracking.timestamps.shift();
        }
    }

    function resetVelocityTracking() {
        velocityTracking.positions = [];
        velocityTracking.timestamps = [];
    }

    // Modal positioning functions
    function setModalPosition(position) {
        // Solo aplicamos límites cuando el modal no se está cerrando
        if (currentState !== MODAL_STATES.CLOSED) {
            const maxPosition = window.innerHeight - initialModalHeight;
            const minPosition = 0;
            position = Math.max(minPosition, Math.min(maxPosition, position));
        }
        modal.style.transform = `translateY(${position}px)`;
    }

    function animateModal(targetPosition, duration = 300) {
        modal.style.transition = `transform ${duration}ms ease-out`;
        setModalPosition(targetPosition);
        
        setTimeout(() => {
            modal.style.transition = '';
        }, duration);
    }

    function updateModalState(newState) {
        currentState = newState;
        
        switch (newState) {
            case MODAL_STATES.FULL:
                animateModal(0);
                modal.classList.add('full-screen');
                break;
            case MODAL_STATES.PARTIAL:
                const partialHeight = window.innerHeight * 0.6;
                animateModal(window.innerHeight - partialHeight);
                modal.classList.remove('full-screen');
                break;
            case MODAL_STATES.CLOSED:
                hideInstructions();
                break;
        }
    }

    function handleTouchStart(e) {
        const touch = e.touches[0];
        startY = touch.pageY;
        currentY = startY;
        initialModalHeight = modal.getBoundingClientRect().height;
        isDragging = true;

        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTapTime;
        if (tapLength < DOUBLE_TAP_DELAY && tapLength > 0) {
            updateModalState(currentState === MODAL_STATES.FULL ? 
                           MODAL_STATES.PARTIAL : 
                           MODAL_STATES.FULL);
        }
        lastTapTime = currentTime;

        resetVelocityTracking();
        trackVelocity(touch.pageY, e.timeStamp);
    }

    function handleTouchMove(e) {
        if (!isDragging) return;
        
        const touch = e.touches[0];
        const deltaY = touch.pageY - startY;
        currentY = touch.pageY;

        trackVelocity(touch.pageY, e.timeStamp);

        const isAtTop = modalContent.scrollTop <= 0;
        const isAtBottom = modalContent.scrollTop + modalContent.clientHeight >= modalContent.scrollHeight;
        
        // Permitir el cierre deslizando hacia arriba
        if (deltaY > 0 && isAtTop) {
            e.preventDefault();
            setModalPosition(deltaY);
        } 
        // Prevenir movimiento hacia arriba solo cuando está en pantalla completa
        else if (currentState === MODAL_STATES.FULL && deltaY < 0) {
            return;
        }
        // Permitir movimiento normal en otros casos
        else if (isAtTop && deltaY > 0 || isAtBottom && deltaY < 0) {
            e.preventDefault();
            setModalPosition(deltaY);
        }
    }

    function handleTouchEnd(e) {
        if (!isDragging) return;
        isDragging = false;

        const velocity = calculateVelocity();
        const deltaY = currentY - startY;

        if (Math.abs(velocity) > VELOCITY_THRESHOLD) {
            if (velocity > 0) {
                updateModalState(MODAL_STATES.CLOSED);
            } else {
                updateModalState(MODAL_STATES.FULL);
            }
        } else if (Math.abs(deltaY) > MIN_DRAG_THRESHOLD) {
            if (deltaY > initialModalHeight * 0.3) {
                updateModalState(MODAL_STATES.CLOSED);
            } else if (deltaY < -initialModalHeight * 0.3) {
                updateModalState(MODAL_STATES.FULL);
            } else {
                updateModalState(MODAL_STATES.PARTIAL);
            }
        } else {
            updateModalState(currentState);
        }
    }

    window.showInstructions = function(title, description, instructions) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalDescription').textContent = description;
        
        const instructionsList = document.getElementById('modalInstructions');
        instructionsList.innerHTML = instructions.split('\n')
            .filter(step => step.trim())
            .map(step => `<li class="instruction-step">${step}</li>`)
            .join('');
        
        modal.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        updateModalState(MODAL_STATES.PARTIAL);
    };

    window.hideInstructions = function() {
        modal.classList.remove('active', 'full-screen');
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
        setModalPosition(window.innerHeight);
        currentState = MODAL_STATES.CLOSED;
    };

    dragHandle.addEventListener('touchstart', handleTouchStart, { passive: false });
    dragHandle.addEventListener('touchmove', handleTouchMove, { passive: false });
    dragHandle.addEventListener('touchend', handleTouchEnd);
    
    modalContent.addEventListener('touchstart', handleTouchStart, { passive: true });
    modalContent.addEventListener('touchmove', handleTouchMove, { passive: false });
    modalContent.addEventListener('touchend', handleTouchEnd);
    
    backdrop.addEventListener('click', hideInstructions);

    window.addEventListener('resize', () => {
        if (currentState !== MODAL_STATES.CLOSED) {
            updateModalState(currentState);
        }
    });
});