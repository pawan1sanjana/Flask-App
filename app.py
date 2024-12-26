from flask import Flask, render_template, jsonify

app = Flask(__name__, static_folder="static", template_folder="templates")

# Sample customer data
CUSTOMERS = [
    {"id": 1, "name": "Customer A", "latitude": 6.9271, "longitude": 79.8612},
    {"id": 2, "name": "Customer B", "latitude": 6.9147, "longitude": 79.9733},
    {"id": 3, "name": "Customer C", "latitude": 6.8650, "longitude": 79.8991},
]

@app.route('/')
def index():
    return render_template('customer_navigation.html')

@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(CUSTOMERS)

if __name__ == '__main__':
    app.run(debug=True)
