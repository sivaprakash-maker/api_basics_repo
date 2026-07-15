from flask import Flask, request, jsonify
import pickle
import numpy as np

# Load trained model
with open("linear_model.pkl", "rb") as f:
    model = pickle.load(f)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Welcome to Linear Regression API"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "year" not in data:
        return jsonify({"error": "Please provide JSON body with key 'year'"}), 400

    x_value = float(data["year"])
    prediction = model.predict(np.array([[x_value]]))[0]

    return jsonify({
        "input": x_value,
        "prediction": prediction
    })


if __name__ == "__main__":
    app.run(debug=True)

""" can you hear me makkale ???
1. First Run this program and ensure the APP is running 
perfectly in localhost
2. then we will test the same using two method
   2.1 one is using postman tool
   2.2 direct via our python application ok !!!"""