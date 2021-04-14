from boxkite.utils.histogram import get_bins


def test_large_sample():
    samples = [i for i in range(1_000_000)]
    edges = get_bins(samples)
    assert len(edges) == 50
