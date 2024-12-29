import json
from flask import Flask, jsonify, request

app = Flask(__name__)

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
            /* Add your CSS styles here (same as your provided HTML code) */
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="floating-input">
            <input type="text" id="customer-ids" placeholder="Enter customer IDs (e.g., 1,2,3)" />
            <button id="set-route">Set Route</button>
        </div>
        <div id="customer-info">
            <h3 id="customer-name"></h3>
            <p id="customer-contact"></p>
            <p id="customer-coordinates"></p>
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

            // Add JavaScript logic here (same as your provided HTML code)
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
