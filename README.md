## boxkite: easily compare training and production ML model distributions

### User Guide

Boxkite allows easy monitoring of model performance in production systems by capturing the model training distribution and comparing it against realtime production distributions via Prometheus.

Boxkite also includes PromQL queries to calculate divergence metrics, such as [KL Divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence) to give you a measure of _how different_ your production traffic is from your training data. This allows you to capture model drift.

#### Logging feature and inference distribution

You may use the model monitoring service to save the distribution of input and model output data to a local file. The default path is `/artefact/histogram.prom` so as to bundle the computed distribution together with the model artefact it trained from. When trained on Bedrock, the zipped `/artefact` directory will be uploaded to user's blob storage bucket in the workload cluster.

```python
import pandas as pd
from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from sklearn.svm import SVC


# User code to load training data
features = pd.DataFrame({'a': [1, 2, 3], 'b': [3, 2, 1]})
model = SVC(probability=True)
model.fit(features, [False, True, False])
inference = model.predict_proba(features)[:, 0]

ModelMonitoringService.export_text(
    features=features.iteritems(),
    inference=inference.tolist(),
)
```

### Monitoring models in production

At serving time, users may import `bdrk[model-monitoring]` library to track various model performance metrics. Anomalies in these metrics can help inform users about model rot.

#### Logging predictions

The model monitoring service may be instantiated in serve.py to log every prediction request for offline analysis. The following example demonstrates how to enable prediction logging in a typical Flask app.

```python
from bedrock_client.bedrock.metrics.service import ModelMonitoringService
from flask import Flask, request
from sklearn.svm import SVC

# User code to load trained model
model = SVC(probability=True)
model.fit([[1, 3], [2, 2], [3, 1]], [False, True, False])

app = Flask(__name__)
monitor = ModelMonitoringService()

@app.route("/", methods=["POST"])
def predict():
    # User code to load features
    features = [2.1, 1.8]
    score = model.predict_proba([features])[:, 0].item()

    monitor.log_prediction(
        request_body=request.json,
        features=features,
        output=score,
    )
    return {"True": score}
```

The logged predictions are persisted in low cost blob store in the workload cluster with a maximum TTL of 1 month. The blob store is partitioned by the endpoint id and the event timestamp according to the following structure: `models/predictions/{endpoint_id}/2020-01-22/1415_{logger_id}-{replica_id}.txt`.

- Endpoint id is the first portion of your domain name hosted on Bedrock
- Replica id is the name of your model server pod
- Logger id is a Bedrock generated name that's unique to the log collector pod

These properties are injected automatically into your model server container as environment variables.

To minimize latency of request handling, all predictions are logged asynchronously in a separate thread pool. We measured the overhead along critical path to be less than 1 ms per request.

#### Tracking feature and inference drift

If training distribution metrics are present in `/artefact` directory, the model monitoring service will also track real time distribution of features and inference results. This is done using the same `log_prediction` call so users don't need to further instrument their serving code.

In order to export the serving distribution metrics, users may add a new `/metrics` endpoint to their Flask app. By default, all metrics are exported in Prometheus exposition format. The example code below shows how to extend the logging predictions example to support this use case.

```python
@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Returns real time feature values recorded by prometheus
    """
    body, content_type = monitor.export_http(
        params=request.args.to_dict(flat=False),
        headers=request.headers,
    )
    return Response(body, content_type=content_type)
```

When deployed in your workload cluster, the `/metrics` endpoint is automatically scraped by Prometheus every minute to store the latest metrics as timeseries data.

## Contributors

The following people have contributed to the original concept and code

- [Han Qiao](https://github.com/sweatybridge)
- [Nguyen Hien Linh](https://github.com/nglinh)
- [Luke Marsden](https://github.com/lukemarsden)

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/basisai/model-monitoring/graphs/contributors).

## Shameless plug

Boxkite is a project from Basis-AI, who offer an MLOps Platform called Bedrock.

[Bedrock](https://bedrock.basis-ai.com) helps data scientists own the end-to-end deployment of machine learning workflows. Boxkite was originally part of the Bedrock client library, but we've spun it out into an open source project so that it's useful for everyone!
