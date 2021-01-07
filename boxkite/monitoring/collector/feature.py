from typing import Iterable, List, Mapping, Optional, Set, Tuple, Type

import numpy as np
from prometheus_client import Metric

from ..frequency import ContinuousVariable, DiscreteVariable, FrequencyMetric, TBin
from .type import Collector


class FeatureDistribution:
    """Defines the parsing rules for feature metric.
    """

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
    def as_discrete(cls, index: int, name: str, bin_to_count: Mapping[TBin, int]) -> Metric:
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

    def _is_discrete(self, val: List[float]) -> bool:
        """Litmus test to determine if val is discrete.

        :param val: Array of positive values
        :type val: List[float]
        :return: Whether input array only contains discrete values
        :rtype: bool
        """
        # Sample size too big, use 1% of max_samples to cap computation at 1ms
        size = len(val)
        if size > 1000:
            size = min(len(val), self.max_samples // 100)
            val = np.random.choice(val, size, replace=False)
        bins = np.unique(val)
        # Caps number of bins to 50
        return len(bins) < 3 or len(bins) * 20 < size

    def _get_bins(self, val: List[float]) -> List[float]:
        """Calculates the optimal bins for prometheus histogram.

        :param val: Array of positive values.
        :type val: List[float]
        :return: Upper bound of each bin (at least 2 bins)
        :rtype: List[float]
        """
        r_min = np.min(val)
        r_max = np.max(val)
        min_bins = 2
        max_bins = 50
        # Calculate bin width using either Freedman-Diaconis or Sturges estimator
        bin_edges = np.histogram_bin_edges(val, bins="auto")
        if len(bin_edges) < min_bins:
            return list(np.linspace(start=r_min, stop=r_max, num=min_bins))
        elif len(bin_edges) <= max_bins:
            return list(bin_edges)
        # Clamp to max_bins by estimating a good bin range to be more robust to outliers
        q75, q25 = np.percentile(val, [75, 25])
        iqr = q75 - q25
        width = 2 * iqr / max_bins
        start = max((q75 + q25) / 2 - iqr, r_min)
        stop = min(start + max_bins * width, r_max)
        # Take the minimum of range and 2x IQR to account for outliers
        edges = list(np.linspace(start=start, stop=stop, num=max_bins))
        prefix = [r_min] if start > r_min else []
        suffix = [r_max] if stop < r_max else []
        return prefix + edges + suffix

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
            size = len(val)
            # Sample without replacement to cap computation to about 3 seconds for 25 features
            if size > self.max_samples:
                size = self.max_samples
                val = np.random.choice(val, size=self.max_samples, replace=False)

            val = val[~np.isnan(val)]
            size_nan = size - len(val)

            if (self.discrete is None and self._is_discrete(val)) or (
                self.discrete is not None and i in self.discrete
            ):
                bins, counts = np.unique(val, return_counts=True)
                bin_to_count = {str(bins[i]): counts[i] for i in range(len(bins))}
                if size_nan > 0:
                    bin_to_count["nan"] = size_nan
                yield FeatureDistribution.as_discrete(
                    index=i, name=name, bin_to_count=bin_to_count
                )
                continue

            val = val[~np.isinf(val)]
            size_inf = size - len(val)

            # Allows negative values as bin edge
            sum_value = np.sum(val)
            if len(val) == 0:
                bin_to_count = {"0.0": 0}
            else:
                bins = self._get_bins(val)
                # Take the negative of all values to use "le" as the bin upper bound
                counts, _ = np.histogram(-val, bins=-np.flip([bins[0]] + bins))
                counts = np.flip(counts)
                bin_to_count = {str(bins[i]): counts[i] for i in range(len(bins))}

            bin_to_count["+Inf"] = size_inf
            yield FeatureDistribution.as_continuous(
                index=i, name=name, bin_to_count=bin_to_count, sum_value=sum_value
            )
