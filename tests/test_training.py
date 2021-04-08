from tempfile import NamedTemporaryFile

from boxkite.monitoring.service import ModelMonitoringService

SAMPLE_TRAINING_DATA = [
    ("first", [3.0, 3.0, 4.0, 5.0, 8.0, 10.0, 13.0, 13.0]),
    ("second", [13.0, 13.0, 14.0, 15.0, 18.0, 20.0, 23.0, None]),
    ("third", [-1.0, 0, 2.0, 5.0, 8.0, 10.0, 13.0, 13.0, float("inf"), float("-inf")]),
    ("fourth", [0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, float("nan"), float("nan")]),
]

EXPECTED_HISTOGRAM_FILE = [
    "# HELP feature_0_value_baseline Baseline values for feature: first\n",
    "# TYPE feature_0_value_baseline histogram\n",
    'feature_0_value_baseline_bucket{le="3.0"} 2.0\n',
    'feature_0_value_baseline_bucket{le="5.5"} 4.0\n',
    'feature_0_value_baseline_bucket{le="8.0"} 5.0\n',
    'feature_0_value_baseline_bucket{le="10.5"} 6.0\n',
    'feature_0_value_baseline_bucket{le="13.0"} 8.0\n',
    'feature_0_value_baseline_bucket{le="+Inf"} 8.0\n',
    "feature_0_value_baseline_count 8.0\n",
    "feature_0_value_baseline_sum 59.0\n",
    "# HELP feature_1_value_baseline Baseline values for feature: second\n",
    "# TYPE feature_1_value_baseline histogram\n",
    'feature_1_value_baseline_bucket{le="13.0"} 2.0\n',
    'feature_1_value_baseline_bucket{le="15.5"} 4.0\n',
    'feature_1_value_baseline_bucket{le="18.0"} 5.0\n',
    'feature_1_value_baseline_bucket{le="20.5"} 6.0\n',
    'feature_1_value_baseline_bucket{le="23.0"} 7.0\n',
    'feature_1_value_baseline_bucket{le="+Inf"} 8.0\n',
    "feature_1_value_baseline_count 8.0\n",
    "feature_1_value_baseline_sum 116.0\n",
    "# HELP feature_2_value_baseline Baseline values for feature: third\n",
    "# TYPE feature_2_value_baseline histogram\n",
    'feature_2_value_baseline_bucket{le="-1.0"} 1.0\n',
    'feature_2_value_baseline_bucket{le="2.5"} 3.0\n',
    'feature_2_value_baseline_bucket{le="6.0"} 4.0\n',
    'feature_2_value_baseline_bucket{le="9.5"} 5.0\n',
    'feature_2_value_baseline_bucket{le="13.0"} 8.0\n',
    'feature_2_value_baseline_bucket{le="+Inf"} 10.0\n',
    "# HELP feature_3_value_baseline_total Baseline values for feature: fourth\n",
    "# TYPE feature_3_value_baseline_total counter\n",
    'feature_3_value_baseline_total{bin="0.0"} 5.0\n',
    'feature_3_value_baseline_total{bin="1.0"} 3.0\n',
    'feature_3_value_baseline_total{bin="nan"} 2.0\n',
]


def test_export_text():
    with NamedTemporaryFile() as temp:
        ModelMonitoringService.export_text(SAMPLE_TRAINING_DATA, path=temp.name)
        histogram_data = temp.readlines()

    for i, line in enumerate(histogram_data):
        assert (
            EXPECTED_HISTOGRAM_FILE[i] == line.decode()
        ), f"Comparison failed at line {i + 1}"
