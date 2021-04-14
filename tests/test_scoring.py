from prometheus_client import generate_latest

from boxkite.monitoring.collector import InferenceHistogramCollector

EXPECTED_HISTOGRAM = [
    "# HELP inference_value_baseline Baseline inference values for test set",
    "# TYPE inference_value_baseline histogram",
    'inference_value_baseline_bucket{le="0.0"} 1.0',
    'inference_value_baseline_bucket{le="0.125"} 13.0',
    'inference_value_baseline_bucket{le="0.25"} 26.0',
    'inference_value_baseline_bucket{le="0.375"} 38.0',
    'inference_value_baseline_bucket{le="0.5"} 51.0',
    'inference_value_baseline_bucket{le="0.625"} 63.0',
    'inference_value_baseline_bucket{le="0.75"} 76.0',
    'inference_value_baseline_bucket{le="0.875"} 88.0',
    'inference_value_baseline_bucket{le="1.0"} 101.0',
    'inference_value_baseline_bucket{le="+Inf"} 101.0',
    "inference_value_baseline_count 101.0",
    "inference_value_baseline_sum 50.49999999999999",
]

EXPECTED_COUNTER = [
    "# HELP inference_value_baseline_total Baseline inference values for test set",
    "# TYPE inference_value_baseline_total counter",
    'inference_value_baseline_total{bin="0.0"} 20.0',
    'inference_value_baseline_total{bin="1.0"} 20.0',
    'inference_value_baseline_total{bin="2.0"} 20.0',
    'inference_value_baseline_total{bin="3.0"} 20.0',
    'inference_value_baseline_total{bin="4.0"} 20.0',
]

EXPECTED_COUNTER_AUTO = [
    "# HELP inference_value_baseline_total Baseline inference values for test set",
    "# TYPE inference_value_baseline_total counter",
    'inference_value_baseline_total{bin="0.0"} 25.0',
    'inference_value_baseline_total{bin="1.0"} 25.0',
    'inference_value_baseline_total{bin="2.0"} 25.0',
    'inference_value_baseline_total{bin="3.0"} 25.0',
]

EXPECTED_REGRESSION = [
    "# HELP inference_value_baseline Baseline inference values for test set",
    "# TYPE inference_value_baseline histogram",
    'inference_value_baseline_bucket{le="25.0"} 1.0',
    'inference_value_baseline_bucket{le="31.25"} 13.0',
    'inference_value_baseline_bucket{le="37.5"} 26.0',
    'inference_value_baseline_bucket{le="43.75"} 38.0',
    'inference_value_baseline_bucket{le="50.0"} 51.0',
    'inference_value_baseline_bucket{le="56.25"} 63.0',
    'inference_value_baseline_bucket{le="62.5"} 76.0',
    'inference_value_baseline_bucket{le="68.75"} 88.0',
    'inference_value_baseline_bucket{le="75.0"} 101.0',
    'inference_value_baseline_bucket{le="+Inf"} 101.0',
    "inference_value_baseline_count 101.0",
    "inference_value_baseline_sum 5050.0",
]


def test_log_inference():
    collector = InferenceHistogramCollector(data=[i / 100 for i in range(101)])
    data = generate_latest(registry=collector)
    for i, line in enumerate(data.decode().strip().split("\n")):
        assert EXPECTED_HISTOGRAM[i] == line, f"Comparison failed at line {i + 1}"


def test_log_class():
    collector = InferenceHistogramCollector(
        data=[i // 20 for i in range(100)], is_discrete=True
    )
    data = generate_latest(registry=collector)
    for i, line in enumerate(data.decode().strip().split("\n")):
        assert EXPECTED_COUNTER[i] == line, f"Comparison failed at line {i + 1}"


def test_log_class_auto():
    collector = InferenceHistogramCollector(data=[i // 25 for i in range(100)])
    data = generate_latest(registry=collector)
    for i, line in enumerate(data.decode().strip().split("\n")):
        assert EXPECTED_COUNTER_AUTO[i] == line, f"Comparison failed at line {i + 1}"


def test_log_regression():
    collector = InferenceHistogramCollector(data=[i / 2 + 25 for i in range(101)])
    data = generate_latest(registry=collector)
    for i, line in enumerate(data.decode().strip().split("\n")):
        assert EXPECTED_REGRESSION[i] == line, f"Comparison failed at line {i + 1}"
