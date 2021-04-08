from typing import Iterable

from prometheus_client import Metric
from prometheus_client.core import InfoMetricFamily

from .type import Collector


class InfoMetricCollector(Collector):
    """Provides metadata about the feature distribution for querying."""

    def __init__(self, metric: Iterable[Metric]):
        """Computes the feature metadata from a list of collected feature histograms.

        :param metric: A list of Prometheus metrics returned from FeatureHistogramCollector
        :type metric: Iterable[Metric]
        """
        self.metric = InfoMetricFamily(
            name="baseline_metrics",
            documentation="Metadata about the baseline training metrics",
            labels=["feature_name", "metric_name", "metric_type"],
        )
        for m in metric:
            start = m.documentation.find(":") + 1
            name = m.documentation[start:].strip()
            self.metric.add_metric(labels=[name, m.name, m.type], value={})

    def describe(self):
        return self.collect()

    def collect(self):
        yield self.metric
