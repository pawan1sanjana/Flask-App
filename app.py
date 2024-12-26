from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for customer locations
customers = [
    {"id": 1, "name": "Customer A", "latitude": 6.9271, "longitude": 79.8612, "contact": "0712345678"},
    {"id": 2, "name": "Customer B", "latitude": 7.8731, "longitude": 80.7718, "contact": "0723456789"},
    {"id": 3, "name": "Customer C", "latitude": 6.0322, "longitude": 80.217, "contact": "0734567890"},
]

# Temporary user credentials
valid_credentials = {"username": "admin", "password": "password123"}

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == valid_credentials["username"] and password == valid_credentials["password"]:
            return redirect(url_for("map"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

# Main map page
@app.route("/map")
def map():
    return render_template("index.html")

# Customer management API
@app.route("/api/customers", methods=["GET", "POST", "PUT", "DELETE"])
def manage_customers():
    if request.method == "GET":
        return jsonify(customers)

    if request.method == "POST":
        new_customer = request.json
        new_customer["id"] = max(customer["id"] for customer in customers) + 1 if customers else 1
        customers.append(new_customer)
        return jsonify({"message": "Customer added successfully"}), 201

    if request.method == "PUT":
        updated_customer = request.json
        for customer in customers:
            if customer["id"] == updated_customer["id"]:
                customer.update(updated_customer)
                return jsonify({"message": "Customer updated successfully"}), 200
        return jsonify({"message": "Customer not found"}), 404

    if request.method == "DELETE":
        customer_id = request.json.get("id")
        global customers
        customers = [customer for customer in customers if customer["id"] != customer_id]
        return jsonify({"message": "Customer deleted successfully"}), 200

# Route for edit page
@app.route("/edit")
def edit():
    return render_template("edit.html")

if __name__ == "__app__":
    app.run(debug=True)
