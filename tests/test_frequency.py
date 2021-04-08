from prometheus_client import generate_latest

from boxkite.monitoring.collector import ComputedMetricCollector
from boxkite.monitoring.collector.feature import FeatureDistribution

EXPECTED_HISTOGRAM = [
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
    # feature_2_value_baseline count and sum are not exported on negative bins
    "# HELP feature_3_value_baseline_total Baseline values for feature: fourth",
    "# TYPE feature_3_value_baseline_total counter",
    'feature_3_value_baseline_total{bin="0.0"} 5.0',
    'feature_3_value_baseline_total{bin="1.0"} 3.0',
    "# HELP feature_4_value_baseline Baseline values for feature: empty",
    "# TYPE feature_4_value_baseline histogram",
    'feature_4_value_baseline_bucket{le="0.0"} 0.0',
    'feature_4_value_baseline_bucket{le="+Inf"} 0.0',
    "feature_4_value_baseline_count 0.0",
    "feature_4_value_baseline_sum 0.0",
    "# HELP feature_5_value_baseline Baseline values for feature: infinity",
    "# TYPE feature_5_value_baseline histogram",
    'feature_5_value_baseline_bucket{le="0.0"} 0.0',
    'feature_5_value_baseline_bucket{le="+Inf"} 2.0',
    "feature_5_value_baseline_count 2.0",
    "feature_5_value_baseline_sum 0.0",
]


def test_log_raw():
    collector = ComputedMetricCollector(
        [
            FeatureDistribution.as_continuous(
                index=0,
                name="first",
                bin_to_count={
                    "3.0": 2.0,
                    "5.5": 2.0,
                    "8.0": 1.0,
                    "10.5": 1.0,
                    "13.0": 2.0,
                },
                sum_value=59,
            ),
            FeatureDistribution.as_continuous(
                index=1,
                name="second",
                bin_to_count={
                    "13.0": 2.0,
                    "15.5": 2.0,
                    "18.0": 1.0,
                    "20.5": 1.0,
                    "23.0": 1.0,
                    "+Inf": 1.0,
                },
                sum_value=116,
            ),
            FeatureDistribution.as_continuous(
                index=2,
                name="third",
                bin_to_count={
                    "-1.0": 1.0,
                    "2.5": 2.0,
                    "6.0": 1.0,
                    "9.5": 1.0,
                    "13.0": 3.0,
                    "+Inf": 2.0,
                },
                sum_value=50,
            ),
            FeatureDistribution.as_discrete(
                index=3, name="fourth", bin_to_count={"0.0": 5, "1.0": 3}
            ),
            FeatureDistribution.as_continuous(
                index=4,
                name="empty",
                bin_to_count={},
            ),
            FeatureDistribution.as_continuous(
                index=5,
                name="infinity",
                bin_to_count={"+Inf": 2},
                sum_value=0,
            ),
        ]
    )
    output = generate_latest(registry=collector)
    for i, line in enumerate(output.decode().strip().split("\n")):
        assert EXPECTED_HISTOGRAM[i] == line, f"Comparison failed at line {i + 1}"
