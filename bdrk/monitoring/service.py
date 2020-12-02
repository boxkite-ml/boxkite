import os
from datetime import datetime, timezone
from typing import Iterable, List, Mapping, Optional, Tuple
from uuid import uuid4

from spanlib.infrastructure.kubernetes.env_var import BEDROCK_SERVER_ID

from .collector import (
    BaselineMetricCollector,
    FeatureHistogramCollector,
    InferenceHistogramCollector,
    InfoMetricCollector,
)
from .collector.type import Collector
from .context import PredictionContext
from .encoder import MetricEncoder
from .exporter import FluentdExporter
from .exporter.type import LogExporter
from .registry import LiveMetricRegistry


class ModelMonitoringService:
    """Entry point for functionalities related to model monitoring in production.
    """

    def __init__(
        self,
        log_exporter: Optional[LogExporter] = None,
        baseline_collector: Optional[BaselineMetricCollector] = None,
    ):
        self._server_id = os.environ.get(BEDROCK_SERVER_ID, "unknown-server")
        self._log_exporter = log_exporter or FluentdExporter()
        self._baseline_collector = baseline_collector or BaselineMetricCollector()
        self._live_metrics = LiveMetricRegistry(metrics=self._baseline_collector.collect())
        self._info_collector = InfoMetricCollector(metric=self._baseline_collector.collect())
        self._metric_encoder = MetricEncoder(
            collectors=[self._baseline_collector, self._live_metrics, self._info_collector]
        )

    def log_prediction(self, request_body: str, features: List[float], output: float) -> str:
        """
        Stores the prediction context asynchronously in the background.

        :param request_body: The body of this prediction request
        :type request_body: str
        :param features: The transformed feature vector
        :type features: List[float]
        :param output: The model output
        :type output: float
        :return: A prediction id that can be used for lookup
        :rtype: str
        """
        pred = PredictionContext(
            request_body=request_body,
            features=features,
            output=output,
            entity_id=uuid4(),
            server_id=self._server_id,
            created_at=datetime.now(tz=timezone.utc),
        )
        self._log_exporter.emit(pred)
        self._live_metrics.observe(pred)
        return pred.prediction_id

    def export_http(
        self,
        params: Optional[Mapping[str, List[str]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Tuple[bytes, str]:
        """Exports the current Prometheus metrics from registry as a http response.

        :param params: The request query params used to filter metrics, defaults to None
        :type params: Optional[Mapping[str, List[str]]], optional
        :param headers: The HTTP request headers used to specify exposition format,
            defaults to Prometheus but also supports OpenMetrics
        :type headers: Optional[Mapping[str, str]], optional
        :return: A tuple of body and content_type
        :rtype: Tuple[bytes, str]
        """
        return self._metric_encoder.as_http(params=params, headers=headers)

    @classmethod
    def export_text(
        cls,
        features: Iterable[Tuple[str, List[float]]],
        inference: Optional[List[float]] = None,
        path: Optional[str] = None,
    ):
        """
        Computes histogram on the input dataset and stores it to a file at specified path.

        :param features: Iterable columns of (name, values)
        :type features: Iterable[Tuple[str, List[float]]]
        :param inference: List of inference results, defaults to None
        :type inference: Optional[List[float]], optional
        :param path: Path to baseline histogram file, defaults to "/artefact/histogram.prom"
        :type path: Optional[str], optional
        """
        collectors: List[Collector] = [FeatureHistogramCollector(data=features)]
        if inference:
            collectors.append(InferenceHistogramCollector(data=inference))
        encoder = MetricEncoder(collectors=collectors)
        path = path or BaselineMetricCollector.DEFAULT_HISTOGRAM_PATH
        with open(path, "wb") as f:
            f.write(encoder.as_text())
