import pickle

from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from bedrock_client.bedrock.metrics.collector import BaselineMetricCollector
from flask import Flask, request

with open("./model.pkl", "rb") as f:
    model = pickle.load(f)

monitor = ModelMonitoringService(
    baseline_collector=BaselineMetricCollector(path="./histogram.prom")
)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def predict():
    features = request.json
    score = model.predict([features])[0]
    pid = monitor.log_prediction(
        request_body=request.data, features=features, output=score,
    )
    return {"result": score, "prediction_id": pid}


@app.route("/metrics", methods=["GET"])
def metrics():
    return monitor.export_http()[0]


if __name__ == "__main__":
    app.run()
