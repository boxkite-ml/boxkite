from logging import getLogger
from os.path import exists
from typing import Optional

from prometheus_client.parser import text_fd_to_metric_families

from .type import Collector


class BaselineMetricCollector(Collector):
    """Collects baseline metrics from a Prometheus file.

    Users may extend this class to fetch baseline metrics from network locations.
    """

    DEFAULT_HISTOGRAM_PATH = "/artefact/histogram.prom"

    def __init__(self, path: Optional[str] = None):
        """Parses baseline metrics from a local file.

        :param path: Path to Prometheus file, defaults to `DEFAULT_HISTOGRAM_PATH`
        :type path: Optional[str], optional
        """
        self.path = path or BaselineMetricCollector.DEFAULT_HISTOGRAM_PATH
        if not exists(self.path):
            getLogger().warn(
                "\nWarning: baseline metrics missing from artefact directory.\n"
                "Your model server should still work but some model monitoring features will not "
                "be availabe. Please refer to our tutorial on generating baseline metrics from "
                "train.py: https://docs.basis-ai.com/getting-started/from-notebook-to-production/"
                "detect-feature-drift#step-1-collect-training-metrics\n\n"
            )

    def describe(self):
        return self.collect()

    def collect(self):
        try:
            with open(self.path, "r") as f:
                for metric in text_fd_to_metric_families(f):
                    # Ignore non-baseline metrics
                    if not metric.name.endswith("_baseline"):
                        continue
                    yield metric
        except FileNotFoundError:
            return []
