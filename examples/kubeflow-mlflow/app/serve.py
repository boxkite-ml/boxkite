import pickle

from flask import Flask, request

with open("./model.pkl", "rb") as f:
    model = pickle.load(f)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def predict():
    features = request.json
    score = model.predict([features])[0]
    return {"result": score}


if __name__ == "__main__":
    app.run()
