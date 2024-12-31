document.addEventListener('DOMContentLoaded', function() {
    // Configuración inicial del mapa
    const map = new maplibregl.Map({
        container: 'map-container',
        style: `https://api.maptiler.com/maps/streets/style.json?key=${maptilerKey}`,
        zoom: 12,
        minZoom: 3,
        maxZoom: 18
    });

    // Añadir controles de navegación
    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    
    // Configuración de colores por severidad
    const severityConfig = {
        1: { color: '#EAB308', label: 'Baja' },
        2: { color: '#F97316', label: 'Media' },
        3: { color: '#EF4444', label: 'Alta' },
        4: { color: '#9333EA', label: 'Crítica' }
    };

    // Configuración de estados
    const statusConfig = {
        'pending': 'Pendiente',
        'in_review': 'En Revisión',
        'verified': 'Verificado',
        'solved': 'Resuelto',
        'rejected': 'Rechazado'
    };

    // Función para crear el HTML del popup
    function createPopupHTML(report) {
        return `
            <div class="p-3 max-w-sm">
                ${report.image_url ? `
                    <img src="${report.image_url}" 
                         class="w-full h-32 object-cover rounded mb-2"
                         alt="Imagen del reporte"
                         onerror="this.onerror=null; this.src='/static/img/placeholder.jpg';">
                ` : ''}
                <div class="flex items-center gap-2 mb-2">
                    <span class="severity-badge-${report.severity} px-2 py-1 rounded-full text-xs">
                        ${severityConfig[report.severity].label}
                    </span>
                    <span class="status-${report.status} px-2 py-1 rounded-full text-xs">
                        ${statusConfig[report.status]}
                    </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">${report.description}</p>
                <div class="text-xs text-gray-500">
                    <i class="fas fa-clock mr-1"></i> ${report.created_at}
                    <br>
                    <i class="fas fa-user mr-1"></i> ${report.user_name}
                </div>
            </div>
        `;
    }

    // Función para agregar marcadores
    function addMarkers(reports) {
        reports.forEach(report => {
            // Validar coordenadas
            if (!isValidCoordinate(report.latitude, report.longitude)) {
                console.warn(`Coordenadas inválidas para el reporte ${report.id}`);
                return;
            }

            // Crear el marcador personalizado
            const markerElement = document.createElement('div');
            markerElement.className = 'custom-marker';
            markerElement.style.cssText = `
                width: 30px;
                height: 30px;
                background-color: ${severityConfig[report.severity].color};
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                cursor: pointer;
                transition: transform 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            // Crear y configurar el popup con opciones ajustadas
            const popup = new maplibregl.Popup({
                offset: {
                    'top': [0, 10],
                    'top-left': [0, 10],
                    'top-right': [0, 10],
                    'bottom': [0, -30],
                    'bottom-left': [0, -30],
                    'bottom-right': [0, -30],
                    'left': [10, 0],
                    'right': [-10, 0]
                },
                closeButton: true,
                closeOnClick: false,
                maxWidth: '300px',
                anchor: 'bottom'
            }).setHTML(createPopupHTML(report));

            // Crear el marcador
            const marker = new maplibregl.Marker({
                element: markerElement,
                anchor: 'center'
            })
            .setLngLat([report.longitude, report.latitude])
            .addTo(map);

            // Manejar eventos del marcador
            let isPopupOpen = false;

            markerElement.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!isPopupOpen) {
                    marker.setPopup(popup);
                    popup.addTo(map);
                    isPopupOpen = true;
                } else {
                    popup.remove();
                    isPopupOpen = false;
                }
            });

            popup.on('close', () => {
                isPopupOpen = false;
            });

            // Eventos hover en desktop
            if (!('ontouchstart' in window)) {
                markerElement.addEventListener('mouseenter', () => {
                    markerElement.style.transform = 'scale(1.1)';
                });

                markerElement.addEventListener('mouseleave', () => {
                    markerElement.style.transform = 'scale(1)';
                });
            }
        });
    }

    // El resto de las funciones permanecen igual
    function isValidCoordinate(lat, lng) {
        return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    }

    function fitMapToMarkers(reports) {
        if (reports.length === 0) return;

        const bounds = new maplibregl.LngLatBounds();
        reports.forEach(report => {
            if (isValidCoordinate(report.latitude, report.longitude)) {
                bounds.extend([report.longitude, report.latitude]);
            }
        });

        map.fitBounds(bounds, {
            padding: { top: 50, bottom: 50, left: 50, right: 50 },
            maxZoom: 15
        });
    }

    // Inicializar el mapa con la ubicación del usuario
    function initializeMapWithLocation() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userLocation = [position.coords.longitude, position.coords.latitude];
                    map.setCenter(userLocation);
                    map.setZoom(13);

                    const reports = JSON.parse(document.getElementById('reports-data').textContent || '[]');
                    const nearbyReports = reports.filter(report => {
                        return calculateDistance(
                            position.coords.latitude,
                            position.coords.longitude,
                            report.latitude,
                            report.longitude
                        ) <= 50;
                    });

                    addMarkers(reports);
                    if (nearbyReports.length > 0) {
                        fitMapToMarkers(nearbyReports);
                    }
                },
                (error) => {
                    console.warn('Error de geolocalización:', error);
                    const reports = JSON.parse(document.getElementById('reports-data').textContent || '[]');
                    addMarkers(reports);
                    fitMapToMarkers(reports);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        } else {
            const reports = JSON.parse(document.getElementById('reports-data').textContent || '[]');
            addMarkers(reports);
            fitMapToMarkers(reports);
        }
    }

    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    function toRad(deg) {
        return deg * (Math.PI/180);
    }

    map.on('load', initializeMapWithLocation);
});


 // Lazy Loading Images
 document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('.lazy-image');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
});

// View Toggle System
const viewToggle = document.getElementById('viewToggle');
const listView = document.querySelector('.list-view');
const mapView = document.querySelector('.map-view');
const createReportBtn = document.querySelector('.create-report-btn');

viewToggle.addEventListener('click', () => {
    listView.classList.toggle('hidden');
    mapView.classList.toggle('visible');
    viewToggle.classList.toggle('map-active');
    createReportBtn.classList.toggle('map-active');
    viewToggle.innerHTML = mapView.classList.contains('visible') 
        ? '<i class="fas fa-list"></i>' 
        : '<i class="fas fa-map-marked-alt"></i>';
});

// Touch Gestures
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeDistance = touchEndX - touchStartX;
    if (Math.abs(swipeDistance) > 100) {
        if (swipeDistance > 0 && mapView.classList.contains('visible')) {
            viewToggle.click();
        } else if (swipeDistance < 0 && !mapView.classList.contains('visible')) {
            viewToggle.click();
        }
    }
}

// Pull to Refresh (ejemplo básico)
let touchStartY = 0;
let touchEndY = 0;

listView.addEventListener('touchstart', e => {
    touchStartY = e.changedTouches[0].screenY;
}, false);

listView.addEventListener('touchend', e => {
    touchEndY = e.changedTouches[0].screenY;
    handlePullToRefresh();
}, false);

function handlePullToRefresh() {
    const pullDistance = touchEndY - touchStartY;
    if (pullDistance > 100 && listView.scrollTop === 0) {
        location.reload();
    }
}