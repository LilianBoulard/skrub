"""
This benchmark tries to understand what's going on inside the `GapEncoder`,
to better understand why it is so slow.

The logic is as follows:
- Tweak the default parameters of the Gap:
  - Set RNG seed
  - Set `min_iter` to 5 (`= max_iter`)
  - Set `max_iter_e_step` to values from 1 to 20
- Before the end of each loop, save the following:
  - `W_change`
  - `W_`
  - `A_`
  - `B_`
- For the visualization, extract from the matrices their:
  - mean
  - determinant (`scipy.linalg.det`)
  - singular values (`s` of `scipy.linalg.svd`)

Date: June 12th 2023
Commit: 7fc998dcafe12764c1c8ddf5b9f271868c720801
"""

import scipy as sp
import numpy as np
import pandas as pd

from typing import List, Dict, Union
from skrub.datasets import fetch_employee_salaries
from argparse import ArgumentParser
from skrub._gap_encoder import (
    GapEncoder,
    GapEncoderColumn,
    _multiplicative_update_h,
    _multiplicative_update_w,
    batch_lookup,
)

from utils import monitor, default_parser, find_result


class ModifiedGapEncoderColumn(GapEncoderColumn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.benchmark_results_: List[Dict[str, Union[np.ndarray, float]]] = []

    def fit(self, X, y=None):
        # Copy parameter rho
        self.rho_ = self.rho
        # Check if first item has str or np.str_ type
        assert isinstance(X[0], str), "Input data is not string. "
        # Make n-grams counts matrix unq_V
        unq_X, unq_V, lookup = self._init_vars(X)
        n_batch = (len(X) - 1) // self.batch_size + 1
        score = self.score(X)
        del X
        # Get activations unq_H
        unq_H = self._get_H(unq_X)

        for n_iter_ in range(self.max_iter):
            # Loop over batches
            for i, (unq_idx, idx) in enumerate(batch_lookup(lookup, n=self.batch_size)):
                if i == n_batch - 1:
                    W_last = self.W_.copy()
                # Update activations unq_H
                unq_H[unq_idx] = _multiplicative_update_h(
                    unq_V[unq_idx],
                    self.W_,
                    unq_H[unq_idx],
                    epsilon=1e-3,
                    max_iter=self.max_iter_e_step,
                    rescale_W=self.rescale_W,
                    gamma_shape_prior=self.gamma_shape_prior,
                    gamma_scale_prior=self.gamma_scale_prior,
                )
                # Update the topics self.W_
                _multiplicative_update_w(
                    unq_V[idx],
                    self.W_,
                    self.A_,
                    self.B_,
                    unq_H[idx],
                    self.rescale_W,
                    self.rho_,
                )

                if i == n_batch - 1:
                    # Compute the norm of the update of W in the last batch
                    W_change = np.linalg.norm(self.W_ - W_last) / np.linalg.norm(W_last)

            print(self.W_.shape, self.A_.shape, self.B_.shape)

            self.benchmark_results_.append(
                {
                    "score": score,
                    "W_change": W_change,
                    "W_": self.W_.copy(),
                    "A_": self.A_.copy(),
                    "B_": self.B_.copy(),
                }
            )

            if (W_change < self.tol) and (n_iter_ >= self.min_iter - 1):
                break  # Stop if the change in W is smaller than the tolerance

        # Update self.H_dict_ with the learned encoded vectors (activations)
        self.H_dict_.update(zip(unq_X, unq_H))
        return self


class ModifiedGapEncoder(GapEncoder):
    fitted_models_: List[ModifiedGapEncoderColumn]

    @property
    def benchmark_results_(self):
        return self.fitted_models_[0].benchmark_results_

    def _create_column_gap_encoder(self):
        return ModifiedGapEncoderColumn(
            ngram_range=self.ngram_range,
            n_components=self.n_components,
            analyzer=self.analyzer,
            gamma_shape_prior=self.gamma_shape_prior,
            gamma_scale_prior=self.gamma_scale_prior,
            rho=self.rho,
            rescale_rho=self.rescale_rho,
            batch_size=self.batch_size,
            tol=self.tol,
            hashing=self.hashing,
            hashing_n_features=self.hashing_n_features,
            max_iter=self.max_iter,
            init=self.init,
            add_words=self.add_words,
            random_state=self.random_state,
            rescale_W=self.rescale_W,
            max_iter_e_step=self.max_iter_e_step,
        )


benchmark_name = "gap_divergence"


@monitor(
    parametrize={
        "max_iter_e_step": range(1, 21),
    },
    save_as=benchmark_name,
)
def benchmark(max_iter_e_step: int):
    """
    Fit a modified `GapEncoder` instance to a single high cardinality column.
    """
    gap = ModifiedGapEncoder(
        min_iter=5,
        max_iter=5,
        max_iter_e_step=max_iter_e_step,
        random_state=0,
    )
    gap.fit(fetch_employee_salaries().X[["employee_position_title"]])

    results: List[Dict[str, Union[float, ...]]] = []
    for i, result in enumerate(gap.benchmark_results_):
        loop_results = {
            "gap_iter": i + 1,
            "W_change": result["W_change"],
            "score": result["score"],
        }
        for matrix_name in ["W_", "A_", "B_"]:
            loop_results.update(
                {
                    f"{matrix_name} mean": result[matrix_name].mean(),
                    # f"{matrix_name} determinant": sp.linalg.det(result[matrix_name]),
                    f"{matrix_name} singular values": sp.linalg.svd(
                        result[matrix_name], compute_uv=False
                    ),
                }
            )
        results.append(loop_results)

    return results


def plot(df: pd.DataFrame):
    pass


if __name__ == "__main__":
    _args = ArgumentParser(
        description="Benchmark for the batch feature of the MinHashEncoder.",
        parents=[default_parser],
    ).parse_args()

    if _args.run:
        df = benchmark()
    else:
        result_file = find_result(benchmark_name)
        df = pd.read_parquet(result_file)

    if _args.plot:
        plot(df)
