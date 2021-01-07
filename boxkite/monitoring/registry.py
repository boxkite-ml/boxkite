from typing import Iterable, List, MutableMapping, Optional

from prometheus_client import Metric

from .collector.feature import FeatureDistribution
from .collector.inference import InferenceDistribution
from .context import PredictionContext
from .frequency import FrequencyMetric


def is_single_value(value):
    return isinstance(value, str) or isinstance(value, dict) or not hasattr(value, "__iter__")


class LiveMetricRegistry:
    """An immutable collection of live metrics that can be incremented as new observations arrive.
    """

    def __init__(self, metrics: Iterable[Metric]):
        """Constructs live metrics based on the given baseline metrics.

        Live metrics are implemented using Prometheus ValueClass and may be incremented as new
        observations arrive. This is different from static metrics from collectors which don't
        change over time.

        Users may export the live metrics current values using the collect method.

        :param metrics: The collection of baseline metrics
        :type metrics: Iterable[Metric]
        """
        self._feature_metrics: MutableMapping[int, FrequencyMetric] = {}
        self._inference_metric: Optional[FrequencyMetric] = None
        for m in metrics:
            if FeatureDistribution.is_supported(m):
                index = FeatureDistribution.extract_index(m)
                frequency = FeatureDistribution.SUPPORTED[m.type].load_frequency(m)
                self._feature_metrics[index] = frequency
            elif InferenceDistribution.is_supported(m):
                self._inference_metric = InferenceDistribution.SUPPORTED[m.type].load_frequency(m)

    def collect(self) -> List[Metric]:
        """Converts live metrics to a static metrics using their current values in the registry.

        :return: The list of converted static metrics
        :rtype: List[Metric]
        """
        metrics = self._inference_metric.metric.collect() if self._inference_metric else []
        for _, v in self._feature_metrics.items():
            metrics += v.metric.collect()
        return metrics

    def observe(self, prediction: PredictionContext):
        """Updates live metrics in the registry with a new observation.

        :param prediction: The new observation
        :type prediction: PredictionContext
        """
        # Do nothing if output is individual class probability
        if self._inference_metric and is_single_value(prediction.output):
            self._inference_metric.observe(prediction.output)
        # Do nothing if features is not iterable
        if is_single_value(prediction.features):
            return
        for i, v in enumerate(prediction.features):
            # Unflattened tensors are unsupported, ignore
            if i in self._feature_metrics and is_single_value(v):
                self._feature_metrics[i].observe(v)
