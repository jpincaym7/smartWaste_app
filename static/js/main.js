// Bottom Navigation Handler
document.addEventListener('DOMContentLoaded', function() {
    const trigger = document.getElementById('bottomNavTrigger');
    const bottomNav = document.getElementById('bottomNav');
    let isOpen = false;

    if (trigger && bottomNav) {
        trigger.addEventListener('click', () => {
            isOpen = !isOpen;
            bottomNav.classList.toggle('active');
            trigger.innerHTML = isOpen ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
            
            // Add rotation animation to the trigger button
            trigger.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
            trigger.style.transition = 'transform 0.3s ease';
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (isOpen && !bottomNav.contains(e.target) && !trigger.contains(e.target)) {
                isOpen = false;
                bottomNav.classList.remove('active');
                trigger.innerHTML = '<i class="fas fa-bars"></i>';
                trigger.style.transform = 'rotate(0deg)';
            }
        });
    }
});

// Enhanced Dropdown Menu Handler
document.addEventListener('DOMContentLoaded', function() {
    const button = document.querySelector('#authUserMenu button');
    const dropdownMenu = document.querySelector('#dropdownMenu');
    
    if (button && dropdownMenu) {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('hidden');
            
            // Add subtle animation
            if (!dropdownMenu.classList.contains('hidden')) {
                dropdownMenu.style.transform = 'scale(1)';
                dropdownMenu.style.opacity = '1';
            } else {
                dropdownMenu.style.transform = 'scale(0.95)';
                dropdownMenu.style.opacity = '0';
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdownMenu.classList.contains('hidden') && 
                !dropdownMenu.contains(e.target) && 
                !button.contains(e.target)) {
                dropdownMenu.classList.add('hidden');
                dropdownMenu.style.transform = 'scale(0.95)';
                dropdownMenu.style.opacity = '0';
            }
        });
    }
});

// Enhanced Toast System
document.addEventListener('DOMContentLoaded', function() {
    function removeToast(toast) {
        toast.classList.add('animate-toast-out');
        setTimeout(() => toast.remove(), 300);
    }

    const closeButtons = document.querySelectorAll('.close-toast');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const toast = button.closest('.toast-message');
            removeToast(toast);
        });
    });

    // Enhanced toast handling
    const toasts = document.querySelectorAll('.toast-message');
    toasts.forEach(toast => {
        let timeoutId;
        let swipeStartX = 0;
        let swipeEndX = 0;

        const startTimer = () => {
            timeoutId = setTimeout(() => removeToast(toast), 5000);
        };

        // Pause/Resume timer on hover
        toast.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
            const progressBar = toast.querySelector('.progress-bar');
            if (progressBar) progressBar.style.animationPlayState = 'paused';
        });

        toast.addEventListener('mouseleave', () => {
            const progressBar = toast.querySelector('.progress-bar');
            if (progressBar) progressBar.style.animationPlayState = 'running';
            startTimer();
        });

        // Enhanced touch gestures
        toast.addEventListener('touchstart', e => {
            swipeStartX = e.touches[0].clientX;
            clearTimeout(timeoutId);
        });

        toast.addEventListener('touchmove', e => {
            if (swipeStartX) {
                const deltaX = e.touches[0].clientX - swipeStartX;
                toast.style.transform = `translateX(${deltaX}px)`;
                toast.style.opacity = 1 - Math.abs(deltaX) / 200;
            }
        });

        toast.addEventListener('touchend', e => {
            swipeEndX = e.changedTouches[0].clientX;
            const deltaX = swipeEndX - swipeStartX;

            if (Math.abs(deltaX) > 100) {
                toast.style.transition = 'all 0.3s ease';
                toast.style.transform = `translateX(${deltaX > 0 ? '200%' : '-200%'})`;
                toast.style.opacity = '0';
                setTimeout(() => removeToast(toast), 300);
            } else {
                toast.style.transition = 'all 0.3s ease';
                toast.style.transform = '';
                toast.style.opacity = '';
                startTimer();
            }

            swipeStartX = 0;
        });

        startTimer();
    });
});

// Enhanced Page Loader
document.addEventListener('DOMContentLoaded', function() {
    const loaderWrapper = document.getElementById('loader-wrapper');
    const content = document.querySelector('.content');
    
    // Add minimum loading time and smooth transition
    setTimeout(() => {
        if (loaderWrapper) {
            loaderWrapper.style.opacity = '0';
            setTimeout(() => {
                loaderWrapper.style.display = 'none';
                if (content) content.style.opacity = '1';
            }, 500);
        }
    }, 1500);
});