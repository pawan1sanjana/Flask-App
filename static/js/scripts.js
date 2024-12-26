const map = L.map('map').setView([6.9271, 79.8612], 8);
let currentLocationMarker = null;
let routingControl = null;
let userLocation = null;

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Store customer data for quick lookup
let customers = [];

// Fetch customer data
fetch('/api/customers')
    .then(response => response.json())
    .then(data => {
        customers = data;

        // Add markers to the map
        customers.forEach(customer => {
            L.marker([customer.latitude, customer.longitude]).addTo(map)
                .bindPopup(`<b>${customer.name}</b><br>Lat: ${customer.latitude}, Lon: ${customer.longitude}`);
        });
    })
    .catch(err => console.error('Error fetching customer data:', err));

// Track real-time location
function updateCurrentLocation() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }

    navigator.geolocation.watchPosition(position => {
        userLocation = [position.coords.latitude, position.coords.longitude];

        if (currentLocationMarker) {
            currentLocationMarker.setLatLng(userLocation);
        } else {
            currentLocationMarker = L.marker(userLocation, { title: 'Your Location' })
                .addTo(map)
                .bindPopup('Your current location');
        }

        map.setView(userLocation, 15);  // Update map to follow the user
    }, err => {
        console.error('Error fetching geolocation:', err);
    });
}

// Re-center map to current location
document.getElementById('recenter').addEventListener('click', () => {
    if (currentLocationMarker) {
        map.setView(currentLocationMarker.getLatLng(), 15);
    } else {
        alert('Current location not available yet.');
    }
});

// Set route based on entered customer IDs
document.getElementById('set-route').addEventListener('click', () => {
    const input = document.getElementById('customer-ids').value.trim();
    const ids = input.split(',').map(id => parseInt(id.trim(), 10));

    // Validate IDs
    const selectedCustomers = ids
        .map(id => customers.find(customer => customer.id === id))
        .filter(customer => customer);

    if (selectedCustomers.length !== ids.length) {
        alert('Invalid customer IDs. Please check and try again.');
        return;
    }

    // Initialize or reset routing control
    if (routingControl) {
        map.removeControl(routingControl);
    }

    // Set waypoints starting from current location
    const waypoints = [
        userLocation,
        ...selectedCustomers.map(customer => L.latLng(customer.latitude, customer.longitude))
    ];

    routingControl = L.Routing.control({
        waypoints: waypoints,
        routeWhileDragging: true,
        createMarker: (i, waypoint) => {
            if (i === 0) {
                return L.marker(waypoint.latLng, { title: 'Start' }).bindPopup('Start Location');
            } else if (i === waypoints.length - 1) {
                return L.marker(waypoint.latLng, { title: 'End' }).bindPopup('End Location');
            } else {
                return L.marker(waypoint.latLng, { title: 'Waypoint' }).bindPopup('Waypoint');
            }
        }
    }).addTo(map);
});

// Enable navigation button
document.getElementById('navigate').addEventListener('click', () => {
    if (!routingControl) {
        alert('Please set the route first.');
        return;
    }

    // Follow the route
    routingControl.getPlan().setRouteIndex(0);  // Start navigation
    alert('Navigation started!');
});

// Start real-time location tracking
updateCurrentLocation();
