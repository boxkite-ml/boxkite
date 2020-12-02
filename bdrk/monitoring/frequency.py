import math
from abc import abstractmethod
from typing import Mapping, Optional, Tuple, Union

from prometheus_client import Counter, Histogram, Metric
from prometheus_client.core import CounterMetricFamily, HistogramMetricFamily
from prometheus_client.metrics import MetricWrapperBase

TBin = Union[str, float, int]


class FrequencyMetric:
    """Base metric type for tracking the frequency of observations occurring in certain ranges
    of values. It will be implemented differently for discrete and continuous variables in ways
    that best preserve their statistical properties.

    This class only deals with streaming updates of frequency counts. It is the caller's
    responsibility to compute optimal bins on training data and provide their frequency counts as
    baseline metrics.

    Useful for tracking feature and inference distributions during training and model serving.
    """

    metric: MetricWrapperBase

    @abstractmethod
    def __init__(self, metric: Metric):
        """Implements conversion between Metric and MetricWrapperBase for various metric type.

        :param metric: The parsed metric
        :type metric: Metric
        """
        raise NotImplementedError

    @staticmethod
    def _get_serving_name_and_documentation_from_baseline(metric: Metric) -> Tuple[str, str]:
        return (
            metric.name.replace("_baseline", ""),
            metric.documentation.replace("Baseline", "Real time"),
        )

    @classmethod
    @abstractmethod
    def dump_frequency(
        cls, metric_name: str, documentation: str, bin_to_count: Mapping[TBin, int]
    ) -> Metric:
        """Dumps frequency count to a static Prometheus metric.

        :param metric_name: Name of the metric (must be the same for training and serving)
        :type metric_name: str
        :param documentation: Help text describing the metric (used for documentation)
        :type documentation: str
        :param bin_to_count: Counts of items in each bin.
        :type bin_to_count: Mapping[Union[str, float, int], int]
        """
        raise NotImplementedError

    @classmethod
    def load_frequency(cls, metric: Metric):
        """Constructs a live frequency metric using buckets defined by static Prometheus metric.

        :param metric: The dumped Prometheus metric.
        :type metric: Metric
        :return: A registered feature metric.
        :rtype: FrequencyMetric
        """
        return cls(metric)

    @abstractmethod
    def observe(self, value: Optional[TBin], labels: Optional[Mapping[str, str]] = None):
        """Adds a new observation to the frequency table by incrementing the counter of the
        appropriate bin.

        :param value: The observed value
        :type value: Union[str, float, int, None]
        :param labels: Additional labels to the observed metric, defaults to None
        :type labels: Optional[Mapping[str, str]], optional
        """
        raise NotImplementedError


class DiscreteVariable(FrequencyMetric):
    """Handles discrete variables, including both numeric and non-numeric values.
    """

    BIN_LABEL = "bin"

    def __init__(self, metric: Metric):
        self.metric = Counter(
            *self._get_serving_name_and_documentation_from_baseline(metric),
            labelnames=(DiscreteVariable.BIN_LABEL,),
            registry=None,
        )
        for sample in metric.samples:
            self.metric.labels(
                **{DiscreteVariable.BIN_LABEL: sample.labels[DiscreteVariable.BIN_LABEL]}
            ).inc(0)

    @classmethod
    def dump_frequency(
        cls, metric_name: str, documentation: str, bin_to_count: Mapping[TBin, int]
    ) -> Metric:
        """Converts a dictionary of bin to count to Prometheus counter.

        :param metric_name: Name of the metric (must be the same for training and serving)
        :type metric_name: str
        :param documentation: Help text describing the metric (used for documentation)
        :type documentation: str
        :param bin_to_count: Counts of items in each bin.
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :return: The converted Prometheus counter metric.
        :rtype: Metric
        """
        counter = CounterMetricFamily(
            name=metric_name, documentation=documentation, labels=(cls.BIN_LABEL,)
        )
        for k, v in bin_to_count.items():
            if isinstance(k, int):
                k = float(k)
            counter.add_metric(labels=[str(k)], value=v)
        return counter

    def observe(self, value: Optional[TBin], labels: Optional[Mapping[str, str]] = None):
        if isinstance(value, int):
            value = float(value)
        base = {"bin": str(value)}
        if labels:
            base.update(labels)
        # Track None, NaN, Inf separately for discrete values
        self.metric.labels(**base).inc()


class ContinuousVariable(FrequencyMetric):
    """Handles continuous variables, including None, NaN, and Inf.
    """

    BIN_LABEL = "le"

    def __init__(self, metric: Metric):
        bins = tuple(
            sample.labels[ContinuousVariable.BIN_LABEL]
            for sample in metric.samples
            if sample.name.endswith("_bucket")
        )
        self.metric = Histogram(
            *self._get_serving_name_and_documentation_from_baseline(metric),
            buckets=bins,
            registry=None,
        )

    @classmethod
    def dump_frequency(
        cls,
        metric_name: str,
        documentation: str,
        bin_to_count: Mapping[TBin, int],
        sum_value: Optional[float] = None,
    ) -> Metric:
        """Converts a dictionary of bin to count to Prometheus histogram.

        :param metric_name: Name of the metric (must be the same for training and serving)
        :type metric_name: str
        :param documentation: Help text describing the metric (used for documentation)
        :type documentation: str
        :param bin_to_count: Counts of items in each bin (must be inserted in ascending order of
            the bin's numerical value). The last bin can be "+Inf" to capture None, NaN, and inf.
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :param sum_value: The total value of all samples, defaults to raw bucket value * count
        :type sum_value: Optional[float], optional
        :return: The converted Prometheus histogram metric.
        :rtype: Metric
        """
        buckets = []
        accumulator = 0
        for k, v in bin_to_count.items():
            accumulator += v
            # Integer values will be handled like floats by Prometheus
            buckets.append([str(k), accumulator])

        if "+Inf" not in bin_to_count:
            buckets.append(["+Inf", buckets[-1][1]])

        return HistogramMetricFamily(
            name=metric_name,
            documentation=documentation,
            buckets=buckets,
            sum_value=sum_value
            or sum(float(k) * v for k, v in bin_to_count.items() if k != "+Inf"),
        )

    def observe(self, value: Optional[TBin], labels: Optional[Mapping[str, str]] = None):
        metric = self.metric.labels(**labels) if labels else self.metric
        if value is None:
            value = "nan"
        try:
            value = float(value)
        except (ValueError, TypeError):
            # TypeError should not be possible with type checking but handling just in case
            value = float("nan")
        # Use +Inf bucket to handle nan (which does not equal to itself!)
        # -inf will be included in the first bucket
        if math.isnan(value) or value == float("inf"):
            metric._buckets[-1].inc(1)
        else:
            metric.observe(value)
