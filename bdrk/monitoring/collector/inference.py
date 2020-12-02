from typing import List, Mapping, Optional, Type

import numpy as np
from prometheus_client import Metric

from ..frequency import ContinuousVariable, DiscreteVariable, FrequencyMetric, TBin
from .type import Collector


class InferenceDistribution:
    """Defines the parsing rules for inference metric.
    """

    BASELINE_NAME_PATTERN = "inference_value_baseline"
    BASELINE_DOC_PATTERN = "Baseline inference values for test set"

    SUPPORTED: Mapping[str, Type[FrequencyMetric]] = {
        "histogram": ContinuousVariable,
        "counter": DiscreteVariable,
    }

    @classmethod
    def is_supported(cls, metric: Metric) -> bool:
        return metric.name.startswith("inference_") and metric.type in cls.SUPPORTED

    @classmethod
    def as_discrete(
        cls, bin_to_count: Mapping[TBin, int], labels: Optional[Mapping[str, str]] = None
    ) -> Metric:
        """Parses the inference metric as a discrete variable, using the given bin to count.

        :param bin_to_count: Counts of items in each bin
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :param labels: Additional labels used for detecting model bias, defaults to None
        :type labels: Optional[Mapping[str, str]], optional
        :return: The converted Prometheus metric
        :rtype: Metric
        """
        return DiscreteVariable.dump_frequency(
            metric_name=cls.BASELINE_NAME_PATTERN,
            documentation=cls.BASELINE_DOC_PATTERN.format(labels),
            bin_to_count=bin_to_count,
        )

    @classmethod
    def as_continuous(
        cls,
        bin_to_count: Mapping[TBin, int],
        sum_value: Optional[float] = None,
        labels: Optional[Mapping[str, str]] = None,
    ) -> Metric:
        """Parses the inference metric as a continuous variable, using the given bin to count.

        :param bin_to_count: Counts of items in each bin
        :type bin_to_count: Mapping[Union[str, float, int], int]
        :param labels: Additional labels used for detecting model bias, defaults to None
        :type labels: Optional[Mapping[str, str]], optional
        :return: The converted Prometheus metric
        :rtype: Metric
        """
        return ContinuousVariable.dump_frequency(
            metric_name=cls.BASELINE_NAME_PATTERN,
            documentation=cls.BASELINE_DOC_PATTERN.format(labels),
            bin_to_count=bin_to_count,
            sum_value=sum_value,
        )


class InferenceHistogramCollector(Collector):
    """Collects metrics related to inference distribution from batch scoring results.

    If is_discrete is True, the inference results will be interpreted as a multiclass
    classification problem.
    """

    def __init__(self, data: List[float], is_discrete: bool = False):
        """Builds the collector using the given data and params.

        Sampling should be done by the user before building the collector to reduce the computation
        time of batch scoring.

        :param data: The full list of inference results to build histogram for
        :type data: List[float]
        :param max_samples: Max number of samples used to calculate histogram, defaults to 100000
        :type max_samples: int, optional
        :param is_discrete: Flag to treat inference results as discrete variable, defaults to False
        :type is_discrete: bool, optional
        """
        self.data: List[float] = data
        self.is_discrete: bool = is_discrete

    def collect(self):
        """Scores the input features using the given model and computes frequency metric on the
        inference result.

        :yield: The converted Prometheus metric for the inference result
        :rtype: Metric
        """
        # Assuming data is float: dtype=float will convert None values to np.nan
        val = np.asarray(self.data, dtype=float)

        if self.is_discrete:
            bins, counts = np.unique(val, return_counts=True)
            bin_to_count = {str(bins[i]): counts[i] for i in range(len(bins))}
            yield InferenceDistribution.as_discrete(bin_to_count=bin_to_count)
            return

        # Assume we are dealing with normalized probability
        sum_value = np.sum(val)
        bins = list(np.linspace(start=0, stop=1, num=51))
        # Take the negative of all values to use "le" as the bin upper bound
        counts, _ = np.histogram(-val, bins=-np.flip([bins[0]] + bins))
        counts = np.flip(counts)
        bin_to_count = {"{:.2f}".format(bins[i]): counts[i] for i in range(len(bins))}

        yield InferenceDistribution.as_continuous(bin_to_count=bin_to_count, sum_value=sum_value)
