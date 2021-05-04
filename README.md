![Boxkite logo](images/boxkite-text.png)

[![PyPI version](https://badge.fury.io/py/boxkite.svg)](https://pypi.python.org/pypi/boxkite/)
[![PyPI license](https://img.shields.io/pypi/l/boxkite.svg)](https://pypi.python.org/pypi/boxkite/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/boxkite.svg)](https://pypi.python.org/pypi/boxkite/)
[![CI workflow](https://github.com/basisai/boxkite/actions/workflows/ci.yml/badge.svg)](https://github.com/basisai/boxkite/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/basisai/boxkite/branch/master/graph/badge.svg?token=0qgLm01XN3)](https://codecov.io/gh/basisai/boxkite)

*{Fast, Correct, Simple} - pick three*

# Easily compare training and production ML data & model distributions

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

If you are interested in alternatives, please refer to our discussions in [FAQ](#FAQ).

## Getting Started

Follow one of our tutorials to easily get started and see how Boxkite works with other tools:

- [Prometheus & Grafana](tutorials/grafana-prometheus.md) in Docker Compose
- [Kubeflow & MLflow](tutorials/kubeflow-mlflow.md) on Kubernetes

See [Installation](installing.md) & [User Guide](using.md) for how to use Boxkite in any environment.

## FAQ

1. Does boxkite support anomaly / outlier detection?

Prometheus has supported outlier detection in time series data since 2015. Once you've setup KL divergence and K-S test metrics, outlier detection can be configured on top using alerting rules. For a detailed example, refer to this tutorial: https://prometheus.io/blog/2015/06/18/practical-anomaly-detection/.

2. Does boxkite support adversarial detection?

Adversarial detection concerns with identifying single OOD (Out Of Distribution) samples rather than comparing whole distributions. The algorithms are also highly model specific. For these reasons, we do not have plans to support them in boxkite at the moment. As an alternative, you may look into Seldon for such capabilities https://github.com/SeldonIO/alibi-detect#adversarial-detection.

3. Does boxkite support concept drifts for text / NLP models?

Not yet. This is still an active research area that we are keeping an eye out for.

4. Does boxkite support tensorflow / pytorch?

Yes, our instrumentation library is framework agnostic. It expects input data to be a `list` or `np.array` regardless of how the model is trained.

## Contributors

The following people have contributed to the original concept and code

- [Han Qiao](https://github.com/sweatybridge)
- [Nguyen Hien Linh](https://github.com/nglinh)
- [Luke Marsden](https://github.com/lukemarsden)
- [Mariappan Ramasamy](https://github.com/Mariappan)

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/basisai/model-monitoring/graphs/contributors).

## Shameless plug

Boxkite is a project from Basis-AI, who offer an MLOps Platform called Bedrock.

[Bedrock](https://basis-ai.com/product) helps data scientists own the end-to-end deployment of machine learning workflows. Boxkite was originally part of the Bedrock client library, but we've spun it out into an open source project so that it's useful for everyone!
