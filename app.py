import json
from flask import Flask, render_template, request, redirect, url_for, jsonify

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

# Temporary user credentials
valid_credentials = {"username": "admin", "password": "password123"}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == valid_credentials["username"] and password == valid_credentials["password"]:
            return redirect(url_for("index"))
        else:
            error_message = "Invalid username or password"
            return render_template("login.html", error=error_message)

    return render_template("login.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/edit")
def edit():
    return render_template("edit.html")

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
