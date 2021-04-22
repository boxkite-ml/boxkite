from typing import List, Mapping, Optional

import numpy as np


def _remove_nans_and_infs(val: np.ndarray):
    return val[~np.isnan(val) & ~np.isinf(val)]


def is_discrete(val: List[float], max_samples: int = 1000) -> bool:
    """Litmus test to determine if val is discrete.

    :param val: Array of values
    :type val: List[float]
    :return: Whether input array only contains discrete values
    :rtype: bool
    """
    # Cap sample size to 1000 to limit computation time to 1ms
    size = min(max_samples, len(val))
    if len(val) > size:
        val = np.random.choice(val, size, replace=False)
    bins = np.unique(val)
    # Caps bin to sample size ratio to 1:20
    return len(bins) < 3 or len(bins) * 20 < size


def get_bins(val: List[float]) -> List[float]:
    """Calculates the optimal bins for prometheus histogram.

    :param val: Array of values
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


def fast_histogram(
    val: List[float],
    discrete: Optional[bool] = None,
    bins: Optional[List[float]] = None,
) -> Mapping[str, float]:
    """Counts the occurrences in each histogram bin, where each value is less than
    or equal to the current bin edge.

    :param val: Array of values
    :type val: List[float]
    :param discrete: Explicit treat val as discrete or continuous value,
        defaults to None which uses is_discrete heuristic
    :type discrete: Optional[bool], optional
    :param bins: Array of values used as bins. Valid only for continuous values
    :type bins: Optional[List[float]]
    :return: Dictionary of histogram bin to count
    :rtype: Mapping[str, float]
    """
    val = np.asarray(val, dtype=float)
    size = len(val)

    # Unique does not work on nan since nan != nan
    val = val[~np.isnan(val)]
    size_nan = size - len(val)
    discrete = is_discrete(val) if discrete is None else discrete

    if discrete:
        bins, counts = np.unique(val, return_counts=True)
        bin_to_count = {str(bins[i]): counts[i] for i in range(len(bins))}
        if size_nan > 0:
            bin_to_count["nan"] = size_nan
        return bin_to_count

    # Counts nan as part of infinity bin
    val = val[~np.isinf(val)]
    size_inf = size - len(val)
    if len(val) == 0:
        return {"+Inf": size_inf}

    # Take the negative of all values to use "le" as the bin upper bound
    bins = bins or get_bins(val)
    counts, _ = np.histogram(-val, bins=-np.flip([bins[0]] + bins))
    counts = np.flip(counts)
    bin_to_count = dict(p for p in zip(map(str, bins), counts))

    # Add infinity bin last to preserve insertion order
    bin_to_count["+Inf"] = size_inf
    return bin_to_count
