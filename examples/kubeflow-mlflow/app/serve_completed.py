import pickle

from boxkite.monitoring.collector import BaselineMetricCollector
from boxkite.monitoring.service import ModelMonitoringService
from flask import Flask, request
import os
import boto3

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html#boto3.set_stream_logger
import logging
boto3.set_stream_logger('boto3.resources', logging.NOTSET)


run_id = os.getenv("MLFLOW_RUN_ID")

if run_id is None:
    print("Loading model and histogram from local files")
    model_file = "./model.pkl"
    histogram_file = "./histogram.prom"

else:
    print("Loading model and histogram from MLflow")
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    local_dir = "/tmp/artifact_downloads"
    if not os.path.exists(local_dir):
        os.mkdir(local_dir)
    local_path = client.download_artifacts(run_id, "", local_dir)
    print("Artifacts downloaded in: {}".format(local_path))
    print("Artifacts: {}".format(os.listdir(local_path)))

    model_file = f"{local_path}/model/model.pkl"
    histogram_file = f"{local_path}/histogram.txt"


with open(model_file, "rb") as f:
    model = pickle.load(f)

monitor = ModelMonitoringService(
    baseline_collector=BaselineMetricCollector(path=histogram_file)
)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def predict():
    features = request.json
    score = model.predict([features])[0]
    pid = monitor.log_prediction(
        request_body=request.data,
        features=features,
        output=score,
    )
    return {"result": score, "prediction_id": pid}


@app.route("/metrics", methods=["GET"])
def metrics():
    return monitor.export_http()[0]


if __name__ == "__main__":
    app.run()
