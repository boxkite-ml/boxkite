from typing import Iterable, List, Mapping, Optional, Set, Tuple, Type

import numpy as np
from prometheus_client import Metric

from boxkite.utils.histogram import fast_histogram

from ..frequency import ContinuousVariable, DiscreteVariable, FrequencyMetric, TBin
from .type import Collector


class FeatureDistribution:
    """Defines the parsing rules for feature metric."""

    BASELINE_NAME_PATTERN = "feature_{0}_value_baseline"
    BASELINE_DOC_PATTERN = "Baseline values for feature: {0}"

    SUPPORTED: Mapping[str, Type[FrequencyMetric]] = {
        "histogram": ContinuousVariable,
        "counter": DiscreteVariable,
    }

    @classmethod
    def extract_index(cls, metric: Metric) -> int:
        return int(metric.name.split("_")[1])

    @classmethod
    def is_supported(cls, metric: Metric) -> bool:
        return metric.name.startswith("feature_") and metric.type in cls.SUPPORTED

    @classmethod
    def as_discrete(
        cls, index: int, name: str, bin_to_count: Mapping[TBin, int]
    ) -> Metric:
        """Parses the feature metric as a discrete variable, using the given bin to count.

        :param index: Index in the feature vector (must be the same for training and serving)
        :type index: int
        :param name: Name of the feature (used for documentation)
        :type name: str
        :param bin_to_count: Counts of items in each bin
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :return: The converted Prometheus metric
        :rtype: Metric
        """
        return DiscreteVariable.dump_frequency(
            metric_name=cls.BASELINE_NAME_PATTERN.format(index),
            documentation=cls.BASELINE_DOC_PATTERN.format(name),
            bin_to_count=bin_to_count,
        )

    @classmethod
    def as_continuous(
        cls,
        index: int,
        name: str,
        bin_to_count: Mapping[TBin, int],
        sum_value: Optional[float] = None,
    ) -> Metric:
        """Parses the feature metric as a continuous variable, using the given bin to count.

        :param index: Index in the feature vector (must be the same for training and serving)
        :type index: int
        :param name: Name of the feature (used for documentation)
        :type name: str
        :param bin_to_count: Counts of items in each bin
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :return: The converted Prometheus metric
        :rtype: Metric
        """
        return ContinuousVariable.dump_frequency(
            metric_name=cls.BASELINE_NAME_PATTERN.format(index),
            documentation=cls.BASELINE_DOC_PATTERN.format(name),
            bin_to_count=bin_to_count,
            sum_value=sum_value,
        )


class FeatureHistogramCollector(Collector):
    """Collects metrics related to feature distribution from in-memory dataset.

    The collector caps the sample size to a configurable `max_samples` to reduce time needed to
    calculate histogram. It also uses heuristics of the data to decide whether a feature column is
    discrete or continuous. Users may override this behaviour using the `discrete` arg.
    """

    def __init__(
        self,
        data: Iterable[Tuple[str, List[float]]],
        max_samples: int = 100000,
        discrete: Optional[Set[int]] = None,
    ):
        """Builds the collector using the given data and params.

        Passing in a set of indices as the discrete parameter will disable heuristics. Every
        feature not in the discrete set will be treated as a continuous variable.

        :param data: Data to build histogram for
        :type data: Iterable[Tuple[str, List[float]]]
        :param max_samples: Max number of samples used to calculate histogram, defaults to 100000
        :type max_samples: int, optional
        :param discrete: Set of indices of discrete features, defaults to None
        :type discrete: Optional[List[int]], optional
        """
        self.data: Iterable[Tuple[str, List[float]]] = data
        self.max_samples: int = max_samples
        self.discrete: Optional[Set[int]] = discrete

    def describe(self):
        """Implements a noop describe method so that when the collector registry is initialized
        using the auto describe param, the collect method will continue to work. We don't want to
        keep the collected data set in memory because it can be as big as a few GB.
        """
        return []

    def collect(self):
        """Calculates histogram bins using numpy and converts to Prometheus metric.

        :yield: The converted Prometheus metric for each feature
        :rtype: Metric
        """
        for i, col in enumerate(self.data):
            name, val = col
            # Assuming data is float. Categorical data should have been one-hot encoded
            # dtype=float will convert None values to np.nan as well
            val = np.asarray(val, dtype=float)

            # Sample without replacement to cap computation to about 3 seconds for 25 features
            if len(val) > self.max_samples:
                val = np.random.choice(val, size=self.max_samples, replace=False)

            discrete = None
            if self.discrete is not None:
                discrete = i in self.discrete
            bin_to_count = fast_histogram(val, discrete=discrete)

            # Continuous histogram will always contain the +Inf bin
            if "+Inf" not in bin_to_count:
                metric = FeatureDistribution.as_discrete(
                    index=i, name=name, bin_to_count=bin_to_count
                )
            else:
                val = val[~np.isinf(val) & ~np.isnan(val)]
                metric = FeatureDistribution.as_continuous(
                    index=i, name=name, bin_to_count=bin_to_count, sum_value=np.sum(val)
                )

            yield metric
