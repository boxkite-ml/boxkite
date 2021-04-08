from datetime import datetime
from os import SEEK_SET
from tempfile import NamedTemporaryFile
from uuid import UUID

from boxkite.monitoring.collector import BaselineMetricCollector
from boxkite.monitoring.service import ModelMonitoringService

BASELINE_HISTOGRAM = [
    "# HELP feature_0_value_baseline Baseline values for feature: first",
    "# TYPE feature_0_value_baseline histogram",
    'feature_0_value_baseline_bucket{le="3.0"} 2.0',
    'feature_0_value_baseline_bucket{le="5.5"} 4.0',
    'feature_0_value_baseline_bucket{le="8.0"} 5.0',
    'feature_0_value_baseline_bucket{le="10.5"} 6.0',
    'feature_0_value_baseline_bucket{le="13.0"} 8.0',
    'feature_0_value_baseline_bucket{le="+Inf"} 8.0',
    "feature_0_value_baseline_count 8.0",
    "feature_0_value_baseline_sum 59.0",
    "# HELP feature_1_value_baseline Baseline values for feature: second",
    "# TYPE feature_1_value_baseline histogram",
    'feature_1_value_baseline_bucket{le="13.0"} 2.0',
    'feature_1_value_baseline_bucket{le="15.5"} 4.0',
    'feature_1_value_baseline_bucket{le="18.0"} 5.0',
    'feature_1_value_baseline_bucket{le="20.5"} 6.0',
    'feature_1_value_baseline_bucket{le="23.0"} 7.0',
    'feature_1_value_baseline_bucket{le="+Inf"} 8.0',
    "feature_1_value_baseline_count 8.0",
    "feature_1_value_baseline_sum 116.0",
    "# HELP feature_2_value_baseline Baseline values for feature: third",
    "# TYPE feature_2_value_baseline histogram",
    'feature_2_value_baseline_bucket{le="-1.0"} 1.0',
    'feature_2_value_baseline_bucket{le="2.5"} 3.0',
    'feature_2_value_baseline_bucket{le="6.0"} 4.0',
    'feature_2_value_baseline_bucket{le="9.5"} 5.0',
    'feature_2_value_baseline_bucket{le="13.0"} 8.0',
    'feature_2_value_baseline_bucket{le="+Inf"} 10.0',
    "feature_2_value_baseline_count 10.0",
    "feature_2_value_baseline_sum 50.0",
    "# HELP feature_3_value_baseline_total Baseline values for feature: fourth",
    "# TYPE feature_3_value_baseline_total counter",
    'feature_3_value_baseline_total{bin="0.0"} 5.0',
    'feature_3_value_baseline_total{bin="1.0"} 3.0',
]

OBSERVED_HISTOGRAM = [
    "# HELP feature_0_value Real time values for feature: first",
    "# TYPE feature_0_value histogram",
    'feature_0_value_bucket{le="3.0"} 1.0',
    'feature_0_value_bucket{le="5.5"} 1.0',
    'feature_0_value_bucket{le="8.0"} 2.0',
    'feature_0_value_bucket{le="10.5"} 2.0',
    'feature_0_value_bucket{le="13.0"} 2.0',
    'feature_0_value_bucket{le="+Inf"} 3.0',
    "feature_0_value_count 3.0",
    "feature_0_value_sum 25.0",
    "# HELP feature_0_value_created Real time values for feature: first",
    "# TYPE feature_0_value_created gauge",
    "feature_0_value_created 1.585658257458352e+09",
    "# HELP feature_1_value Real time values for feature: second",
    "# TYPE feature_1_value histogram",
    'feature_1_value_bucket{le="13.0"} 1.0',
    'feature_1_value_bucket{le="15.5"} 1.0',
    'feature_1_value_bucket{le="18.0"} 3.0',
    'feature_1_value_bucket{le="20.5"} 3.0',
    'feature_1_value_bucket{le="23.0"} 3.0',
    'feature_1_value_bucket{le="+Inf"} 3.0',
    "feature_1_value_count 3.0",
    "feature_1_value_sum 33.0",
    "# HELP feature_1_value_created Real time values for feature: second",
    "# TYPE feature_1_value_created gauge",
    "feature_1_value_created 1.585658257458511e+09",
    "# HELP feature_2_value Real time values for feature: third",
    "# TYPE feature_2_value histogram",
    'feature_2_value_bucket{le="-1.0"} 1.0',
    'feature_2_value_bucket{le="2.5"} 2.0',
    'feature_2_value_bucket{le="6.0"} 2.0',
    'feature_2_value_bucket{le="9.5"} 3.0',
    'feature_2_value_bucket{le="13.0"} 3.0',
    'feature_2_value_bucket{le="+Inf"} 3.0',
    "feature_2_value_count 3.0",
    "# HELP feature_2_value_created Real time values for feature: third",
    "# TYPE feature_2_value_created gauge",
    "feature_2_value_created 1.5856582574586399e+09",
    "# HELP feature_3_value_total Real time values for feature: fourth",
    "# TYPE feature_3_value_total counter",
    'feature_3_value_total{bin="0.0"} 1.0',
    'feature_3_value_total{bin="1.0"} 2.0',
    "# HELP feature_3_value_created Real time values for feature: fourth",
    "# TYPE feature_3_value_created gauge",
    'feature_3_value_created{bin="0.0"} 1.5856582574587672e+09',
    'feature_3_value_created{bin="1.0"} 1.585658257458787e+09',
]

METADATA_HISTOGRAM = [
    "# HELP baseline_metrics_info Metadata about the baseline training metrics",
    "# TYPE baseline_metrics_info gauge",
    'baseline_metrics_info{feature_name="first",metric_name="feature_0_value_baseline",metric_type="histogram"} 1.0',  # noqa: E501
    'baseline_metrics_info{feature_name="second",metric_name="feature_1_value_baseline",metric_type="histogram"} 1.0',  # noqa: E501
    'baseline_metrics_info{feature_name="third",metric_name="feature_2_value_baseline",metric_type="histogram"} 1.0',  # noqa: E501
    'baseline_metrics_info{feature_name="fourth",metric_name="feature_3_value_baseline",metric_type="counter"} 1.0',  # noqa: E501
]

SAMPLE_SERVING_DATA = [
    ([1, 1, 1, 1.0], 0.5),
    ([8, 16, -2, 0.0], 0.8),
    ([16, 16, 8, 1.0], 0.6),
]


def test_log_prediction():
    with NamedTemporaryFile() as temp:
        temp.writelines(line.encode() + b"\n" for line in BASELINE_HISTOGRAM)
        temp.seek(0, SEEK_SET)
        service = ModelMonitoringService(
            baseline_collector=BaselineMetricCollector(path=temp.name)
        )

        for feature, inference in SAMPLE_SERVING_DATA:
            pid = service.log_prediction(
                request_body="test", features=feature, output=inference
            )
            # Validate prediction id
            server_id, timestamp, entity_id = pid.split("/")
            assert server_id == "unknown-server"
            datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
            assert str(UUID(entity_id)) == entity_id

        body, _ = service.export_http()

    # Validate response body
    parsed = body.decode().strip().split("\n")
    for i, expected in enumerate(
        BASELINE_HISTOGRAM + OBSERVED_HISTOGRAM + METADATA_HISTOGRAM
    ):
        if "_created" in expected:
            continue
        assert expected == parsed[i], f"Comparison failed at line {i + 1}"
