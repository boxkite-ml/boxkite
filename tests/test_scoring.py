from prometheus_client import generate_latest

from boxkite.monitoring.collector import InferenceHistogramCollector

EXPECTED_HISTOGRAM = [
    "# HELP inference_value_baseline Baseline inference values for test set",
    "# TYPE inference_value_baseline histogram",
    'inference_value_baseline_bucket{le="0.00"} 1.0',
    'inference_value_baseline_bucket{le="0.02"} 3.0',
    'inference_value_baseline_bucket{le="0.04"} 5.0',
    'inference_value_baseline_bucket{le="0.06"} 7.0',
    'inference_value_baseline_bucket{le="0.08"} 9.0',
    'inference_value_baseline_bucket{le="0.10"} 11.0',
    'inference_value_baseline_bucket{le="0.12"} 13.0',
    'inference_value_baseline_bucket{le="0.14"} 15.0',
    'inference_value_baseline_bucket{le="0.16"} 17.0',
    'inference_value_baseline_bucket{le="0.18"} 19.0',
    'inference_value_baseline_bucket{le="0.20"} 21.0',
    'inference_value_baseline_bucket{le="0.22"} 23.0',
    'inference_value_baseline_bucket{le="0.24"} 25.0',
    'inference_value_baseline_bucket{le="0.26"} 27.0',
    'inference_value_baseline_bucket{le="0.28"} 29.0',
    'inference_value_baseline_bucket{le="0.30"} 31.0',
    'inference_value_baseline_bucket{le="0.32"} 33.0',
    'inference_value_baseline_bucket{le="0.34"} 35.0',
    'inference_value_baseline_bucket{le="0.36"} 37.0',
    'inference_value_baseline_bucket{le="0.38"} 39.0',
    'inference_value_baseline_bucket{le="0.40"} 41.0',
    'inference_value_baseline_bucket{le="0.42"} 43.0',
    'inference_value_baseline_bucket{le="0.44"} 45.0',
    'inference_value_baseline_bucket{le="0.46"} 47.0',
    'inference_value_baseline_bucket{le="0.48"} 49.0',
    'inference_value_baseline_bucket{le="0.50"} 51.0',
    'inference_value_baseline_bucket{le="0.52"} 53.0',
    'inference_value_baseline_bucket{le="0.54"} 55.0',
    'inference_value_baseline_bucket{le="0.56"} 57.0',
    'inference_value_baseline_bucket{le="0.58"} 59.0',
    'inference_value_baseline_bucket{le="0.60"} 61.0',
    'inference_value_baseline_bucket{le="0.62"} 63.0',
    'inference_value_baseline_bucket{le="0.64"} 65.0',
    'inference_value_baseline_bucket{le="0.66"} 67.0',
    'inference_value_baseline_bucket{le="0.68"} 69.0',
    'inference_value_baseline_bucket{le="0.70"} 71.0',
    'inference_value_baseline_bucket{le="0.72"} 73.0',
    'inference_value_baseline_bucket{le="0.74"} 75.0',
    'inference_value_baseline_bucket{le="0.76"} 77.0',
    'inference_value_baseline_bucket{le="0.78"} 79.0',
    'inference_value_baseline_bucket{le="0.80"} 81.0',
    'inference_value_baseline_bucket{le="0.82"} 83.0',
    'inference_value_baseline_bucket{le="0.84"} 85.0',
    'inference_value_baseline_bucket{le="0.86"} 87.0',
    'inference_value_baseline_bucket{le="0.88"} 89.0',
    'inference_value_baseline_bucket{le="0.90"} 91.0',
    'inference_value_baseline_bucket{le="0.92"} 93.0',
    'inference_value_baseline_bucket{le="0.94"} 95.0',
    'inference_value_baseline_bucket{le="0.96"} 97.0',
    'inference_value_baseline_bucket{le="0.98"} 99.0',
    'inference_value_baseline_bucket{le="1.00"} 101.0',
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
