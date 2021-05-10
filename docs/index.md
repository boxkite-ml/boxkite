# Easy Open Source ML Monitoring

![Boxkite logo](images/boxkite-text.png){: style="width:300px" }

Boxkite makes it easy to monitor ML models in production and integrate into your existing workflows. It aims to be simple, flexible, and reliable.

Boxkite allows easy monitoring of model behavior in production systems by capturing the model training distributions and comparing them against realtime production distributions via Prometheus and Grafana:

![Grafana dashboard](images/model-metrics.png "Grafana Dashboard")

Boxkite also includes PromQL queries to calculate divergence metrics, such as [KL Divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence) to give you a measure of _how different_ your production traffic is from your training data. This allows you to capture model and data drift.

## Demo!

<style>
.video-wrapper {
  position: relative;
  display: block;
  height: 0;
  padding: 0;
  overflow: hidden;
  padding-bottom: 56.25%;
  border: 1px solid gray;
}
.video-wrapper > iframe {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>

<div class="video-wrapper">
  <iframe width="1280" height="720" src="https://www.youtube.com/embed/zz-0Yn6_eMQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>


## Goals

Boxkite is an instrumentation library designed from ground up for tracking **concept drift** in HA (Highly Available) model servers. It integrates well with existing DevOps tools (ie. Grafana, Prometheus, fluentd, kubeflow, etc.), and scales horizontally to multiple replicas with no code or infrastructure change.

- **Fast**
    - 0.5 seconds to process 1 million data points (training)
    - Sub millisecond p99 latency (serving)
    - Supports sampling for large data sets
- **Correct**
    - Aggregates histograms from multiple server replicas (using PromQL)
    - Separate counters for discrete and continuous variables (ie. categorical and numeric features)
    - Initialises serving histogram bins from training data set (based on Freedman-Diaconis rule)
    - Handles unseen data, `nan`, `None`, `inf`, and negative values
- **Simple**
    - One metric for each counter type (no confusion over which metric to choose)
    - Default configuration supports both feature and inference monitoring (easy to setup)
    - Small set of dependencies: prometheus, numpy, and fluentd
    - Extensible metric system (support for image classification coming soon)

Some non-goals of this project are:

- Adversarial detection

If you are interested in alternatives, please refer to our discussions in [FAQ](faqs.md).

## Getting Started

Follow one of our tutorials to easily get started and see how Boxkite works with other tools:

- [Prometheus & Grafana](tutorials/grafana-prometheus.md) in Docker Compose
- [Kubeflow & MLflow](tutorials/kubeflow-mlflow.md) on Kubernetes with **easy online test drive in the browser**

See [Installation](installing.md) & [User Guide](using.md) for how to use Boxkite in any environment.

## Contributors

The following people have contributed to the original concept and code

- [Han Qiao](https://github.com/sweatybridge)
- [Nguyen Hien Linh](https://github.com/nglinh)
- [Luke Marsden](https://github.com/lukemarsden)

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/basisai/model-monitoring/graphs/contributors).

## Shameless Plug

Boxkite is a project from Basis-AI, who offer an MLOps Platform called Bedrock.

[Bedrock](https://basis-ai.com/product) helps data scientists own the end-to-end deployment of machine learning workflows. Boxkite was originally part of the Bedrock client library, but we've spun it out into an open source project so that it's useful for everyone!
