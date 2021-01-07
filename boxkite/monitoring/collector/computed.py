from typing import Iterable

from prometheus_client import Metric

from .type import Collector


class ComputedMetricCollector(Collector):
    """A wrapper for manually computed baseline distribution metrics.
    """

    def __init__(self, metric: Iterable[Metric]):
        """Wraps user computed metrics in a collector interface for consumption by other systems.

        :param metric: A list of Prometheus metrics returned from FrequencyMetric.dump_frequency
        :type metric: Iterable[Metric]
        """
        self.metric = metric

    def describe(self):
        return self.collect()

    def collect(self):
        for m in self.metric:
            yield m
