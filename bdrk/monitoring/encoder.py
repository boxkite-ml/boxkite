import os
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple

from prometheus_client import CollectorRegistry, generate_latest
from prometheus_client.exposition import choose_encoder, openmetrics
from prometheus_client.metrics import MetricWrapperBase
from prometheus_client.multiprocess import MultiProcessCollector

from .registry import LiveMetricRegistry


class MetricEncoder:
    """Encodes Prometheus metrics from collectors as either a byte string or HTTP response.
    """

    PROMETHEUS = generate_latest
    OPEN_METRICS = openmetrics.generate_latest

    def __init__(self, collectors: Iterable[Any]):
        """Builds a metric encoder using the given list of collectors. A collector is broadly
        defined here as any type that implements the `collect` method.

        :param collectors: The collectors to fetch metrics from
        :type collectors: Iterable[Any]
        """
        self._registry = CollectorRegistry(auto_describe=True)

        # Always use a new registry for collecting mmapped files under multiprocess mode
        if "prometheus_multiproc_dir" in os.environ:
            MultiProcessCollector(self._registry)
            # Do not double register metrics that implement MultiProcessValue
            # See: prometheus_client/values.py#L31
            collectors = filter(
                lambda c: not isinstance(c, LiveMetricRegistry)
                and not isinstance(c, MetricWrapperBase)
                and hasattr(c, "collect"),
                collectors,
            )

        for c in collectors:
            self._registry.register(c)

    def as_text(
        self, names: Optional[Iterable[str]] = None, encoder: Optional[Callable] = None
    ) -> bytes:
        """Encodes selected metrics in the registry as a byte string.

        Users may choose between PROMETHEUS (default) and OPEN_METRICS encoder, and may optionally
        specify a list of metric names to export.

        :param names: Set of metric names to include, defaults to None
        :type names: Optional[Set[str]], optional
        :param encoder: The metrics serializer, defaults to None
        :type encoder: Optional[Callable], optional
        :return: Serialized metrics
        :rtype: bytes
        """
        encoder = encoder or MetricEncoder.PROMETHEUS
        registry = self._registry.restricted_registry(names) if names else self._registry
        return encoder(registry)

    def as_http(
        self,
        params: Optional[Mapping[str, List[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Tuple[bytes, str]:
        """Encodes all metrics in the registry as a HTTP response.

        The metric selection and encoding are extracted from the query param and accept header
        respectively. Reference implementation: `prometheus_client.exposition.MetricsHandler`

        :param params: The request query params, defaults to None
        :type params: Optional[Mapping[str, List[str]]], optional
        :param headers: The HTTP request headers, defaults to None
        :type headers: Optional[Mapping[str, str]], optional
        :return: A tuple of response body and content type
        :rtype: Tuple[bytes, str]
        """
        params = params or {}
        headers = headers or {}
        encoder, content_type = choose_encoder(headers.get("Accept"))
        body = self.as_text(names=params.get("name[]"), encoder=encoder)
        return body, content_type
