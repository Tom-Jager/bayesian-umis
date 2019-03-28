"""
Helper functions for building the mfa mathematical model from stocks and
flows

Taken from Lupton, R. C. and Allwood, J. M. (2018), Incremental Material Flow
Analysis with Bayesian Inference. Journal of Industrial Ecology, 22: 1352-1364.
doi:10.1111/jiec.12698

https://github.com/ricklupton/bayesian-mfa-paper
"""

from typing import List, Tuple

import numpy as np

def make_distribution_tcs(
        shares: List[float],
        with_stddev: Tuple[int, float] = None) -> List[float]:
    """
    Args
    ----
    shares (list(float)): Share of process throughput to output
    std_dev (tuple(int, float)): Std dev value for one of the share values
    """
    # normalise
    factor = sum(shares)
    shares = np.array(shares) / factor

    if with_stddev is not None:
        i, stddev = with_stddev
        stddev /= factor
        mi = shares[i]
        limit = np.sqrt(mi * (1 - mi) / (1 + len(shares)))
        if stddev > limit:
            raise ValueError(
                'stddev is too high (%.2g > %.2g)' % (stddev, limit))
        concentration = mi * (1 - mi) / stddev**2 - 1
        if not np.isfinite(concentration):
            concentration = 1e10

        return concentration * shares

    else:
        return shares


def get_process_name(
        pos_to_diagram: str,
        process_name: str,
        space_name: str) -> str:
    """ 
    Get process name

    Args
    ----
    pos_to_diagram (str): 'EXT' if process is external, 'INT' if internal
    process_name (str): Name of process
    space_name (str): Name of process reference space
    """

    # Umis mentions the importance of having a unique name for each process
    # We are assuming this exists for readability

    # P_{process_name}_S_{flow_space}

    process_name = "P_{}_S_{}_{}".format(
        process_name, space_name, pos_to_diagram)

    return process_name
