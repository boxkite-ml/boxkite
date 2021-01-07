from abc import abstractmethod
from typing import Iterable

from prometheus_client import Metric


class Collector:
    """Defines the collector interface for generating static Prometheus metrics.

    Users who wish to load metric from different data sources should inherit from this class.

    When registered directly with Prometheus client's CollectorRegistry, users may optionally
    define a `describe` method that returns metrics in the same format as `collect`, but without
    including any samples. This method will be used for detecting duplicate metrics and should be
    much cheaper than calling `collect` directly. For more information, please see:

    https://github.com/prometheus/client_python#custom-collectors
    """

    @abstractmethod
    def collect(self) -> Iterable[Metric]:
        raise NotImplementedError
