import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# Path to the JSON file storing customer data
CUSTOMERS_FILE = "customers.json"

def load_customers():
    """Load customer data from the JSON file."""
    try:
        with open(CUSTOMERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_customers(customers):
    """Save customer data to the JSON file."""
    with open(CUSTOMERS_FILE, "w") as file:
        json.dump(customers, file, indent=4)

@app.route("/")
def index():
    # Serve the HTML content directly from the Flask app
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Customer Navigation Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
            }
            #map {
                height: 100vh;
                width: 100vw;
            }
            .floating-input {
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                background-color: rgba(255, 255, 255, 0.95);
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                width: calc(100% - 20px);
                max-width: 400px;
                display: flex;
                gap: 10px;
                z-index: 1000;
            }
            .floating-input input {
                flex: 1;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                outline: none;
            }
            .floating-input button {
                padding: 10px;
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .floating-buttons-container {
                position: fixed;
                left: 20px;
                bottom: 80px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .floating-button, #navigate, #recenter {
                background-color: white;
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                cursor: pointer;
                transition: transform 0.3s ease-in-out;
            }
            .floating-button:hover, #navigate:hover, #recenter:hover {
                transform: scale(1.1);
            }
            #recenter img, #navigate img, .floating-button img {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="floating-input">
            <input type="text" id="customer-ids" placeholder="Enter customer IDs (e.g., 1,2,3)" />
            <button id="set-route">Set Route</button>
        </div>

        <div class="floating-buttons-container">
            <button class="floating-button" id="recenter">
                <img src="https://cdn-icons-png.flaticon.com/512/929/929430.png" alt="Re-center">
            </button>
            <button id="navigate">
                <img src="https://cdn-icons-png.flaticon.com/512/684/684908.png" alt="Navigate">
            </button>
        </div>

        <script>
            const map = L.map('map', { zoomControl: false }).setView([6.1677, 80.1864], 10);

            const bounds = L.latLngBounds(
                [5.930, 79.850], 
                [6.330, 80.500]
            );

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
            map.setMaxBounds(bounds);
            map.setMinZoom(10);
            map.fitBounds(bounds);

            L.control.zoom({ position: 'bottomright' }).addTo(map);

            let customers = [];
            fetch('/api/customers')
                .then(response => response.json())
                .then(data => {
                    customers = data;
                    customers.forEach(customer => {
                        const marker = L.marker([customer.latitude, customer.longitude], {
                            icon: L.icon({
                                iconUrl: 'https://cdn-icons-png.flaticon.com/512/252/252025.png',
                                iconSize: [32, 32],
                            }),
                        }).addTo(map).bindPopup(`<b>${customer.name}</b>`);
                    });
                })
                .catch(err => console.error('Error fetching customer data:', err));

            let currentLocationMarker = null;
            let userLocation = null;

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
                        currentLocationMarker = L.marker(userLocation, {
                            icon: L.icon({
                                iconUrl: 'https://cdn-icons-png.flaticon.com/512/727/727399.png',
                                iconSize: [32, 32],
                            }),
                        }).addTo(map);
                    }
                });
            }

            document.getElementById('recenter').addEventListener('click', () => {
                if (currentLocationMarker) {
                    map.flyTo(currentLocationMarker.getLatLng(), 15);
                } else {
                    alert('Current location not available yet.');
                }
            });

            updateCurrentLocation();
        </script>
    </body>
    </html>
    """

@app.route("/api/customers", methods=["GET", "POST", "PUT"])
def manage_customers():
    customers = load_customers()

    if request.method == "GET":
        return jsonify(customers)

    if request.method == "POST":
        new_customer = request.json
        new_customer["id"] = max(customer["id"] for customer in customers) + 1 if customers else 1
        customers.append(new_customer)
        save_customers(customers)
        return jsonify({"message": "Customer added successfully"}), 201

    if request.method == "PUT":
        updated_customer = request.json
        for customer in customers:
            if customer["id"] == updated_customer["id"]:
                customer.update(updated_customer)
                save_customers(customers)
                return jsonify({"message": "Customer updated successfully"}), 200
        return jsonify({"message": "Customer not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
