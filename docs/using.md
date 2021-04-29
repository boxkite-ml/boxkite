# User Guide

Boxkite is an easy way to track model and data drift for Machine Learning models.

**Data drift:** how did the input data vary from when I trained my model to what it's getting in production?

**Model drift:** how are the predictions/classifications that my model is making vary from when it was trained to what it's predicting in production?


You use boxkite by doing three things:

## 1. When you train the model

Tell boxkite your training time data (features) and predictions on the training set.

```python
bunch = load_diabetes()
X_train, X_test, Y_train, Y_test = train_test_split(
    bunch.data, bunch.target
)
model = LinearRegression()
model.fit(X_train, Y_train)

print("Score: %.2f" % model.score(X_test, Y_test))
with open("./model.pkl", "wb") as f:
    pickle.dump(model, f)

# features = [("age", [33, 23, 54, ...]), ("sex", [0, 1, 0]), ...]
features = zip(*[bunch.feature_names, X_train.T])

Y_pred = model.predict(X_test)
inference = list(Y_pred)

ModelMonitoringService.export_text(
    features=features, inference=inference, path="./histogram.txt", # <-- HERE
)
mlflow.log_artifact("./histogram.txt")
```

## 2. When you run the model

Record features & predictions at runtime.

```python
@app.route("/", methods=["POST"])
def predict():
    features = request.json
    score = model.predict([features])[0]
    pid = monitor.log_prediction( # <-- HERE
        request_body=request.data,
        features=features,
        output=score,
    )
    return {"result": score, "prediction_id": pid}

```

## 3. Expose the metrics

```python
@app.route("/metrics", methods=["GET"])
def metrics():
    return monitor.export_http()[0]

```

Simply expose metrics and then use our Grafana dashboard!

See our tutorials for full worked examples with sample code:

- [Prometheus & Grafana](tutorials/grafana-prometheus.md) in Docker Compose
- [Kubeflow & MLflow](tutorials/kubeflow-mlflow.md) on Kubernetes
