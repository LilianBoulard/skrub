import copy
import random
from string import ascii_lowercase

import joblib
import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal
from sklearn.exceptions import NotFittedError
from sklearn.utils._testing import skip_if_no_parallel

from skrub import MinHashEncoder

from .utils import generate_data


@pytest.mark.parametrize(
    ["hashing", "minmax_hash"],
    [
        ("fast", True),
        ("fast", False),
        ("murmur", False),
    ],
)
def test_minhash_encoder(hashing, minmax_hash) -> None:
    X = np.array(["al ice", "b ob", "bob and alice", "alice and bob"])[:, None]
    # Test output shape
    encoder = MinHashEncoder(n_components=2, hashing=hashing)
    encoder.fit(X)
    y = encoder.transform(X)
    assert y.shape == (4, 2), str(y.shape)
    assert len(set(y[0])) == 2

    # Test that using the same seed returns the same output
    encoder2 = MinHashEncoder(n_components=2, hashing=hashing)
    encoder2.fit(X)
    y2 = encoder2.transform(X)
    assert_array_equal(y, y2)

    # Test min property
    if not minmax_hash:
        X_substring = [x[: x.find(" ")] for x in X[:, 0]]
        X_substring = np.array(X_substring)[:, None]
        encoder3 = MinHashEncoder(n_components=2, hashing=hashing)
        encoder3.fit(X_substring)
        y_substring = encoder3.transform(X_substring)
        np.testing.assert_array_less(y - y_substring, 0.001)


def test_multiple_columns() -> None:
    """
    This test aims at verifying that fitting multiple columns
    with the MinHashEncoder will not produce an error, and will
    encode the column independently.
    """
    X = pd.DataFrame(
        [
            ("bird", "parrot"),
            ("bird", "nightingale"),
            ("mammal", "monkey"),
            ("mammal", np.nan),
        ],
        columns=("class", "type"),
    )
    X1 = X[["class"]]
    X2 = X[["type"]]
    fit1 = MinHashEncoder(n_components=30).fit_transform(X1)
    fit2 = MinHashEncoder(n_components=30).fit_transform(X2)
    fit = MinHashEncoder(n_components=30).fit_transform(X)
    assert_array_equal(np.array([fit[:, :30], fit[:, 30:60]]), np.array([fit1, fit2]))


def test_input_type() -> None:
    # Numpy array
    X = np.array(["alice", "bob"])[:, None]
    enc = MinHashEncoder(n_components=2)
    enc.fit_transform(X)
    # List
    X = [["alice"], ["bob"]]
    enc = MinHashEncoder(n_components=2)
    enc.fit_transform(X)


@pytest.mark.parametrize(
    ["hashing", "minmax_hash"],
    [
        ("fast", True),
        ("fast", False),
        ("murmur", False),
    ],
)
def test_encoder_params(hashing, minmax_hash) -> None:
    X = generate_data(n_samples=20)
    enc = MinHashEncoder(
        n_components=50, hashing=hashing, minmax_hash=minmax_hash, ngram_range=(3, 3)
    )
    enc.fit(X)
    y = enc.transform(X)
    assert y.shape == (len(X), 50)
    X2 = np.array([["a", "", "c"]]).T
    y2 = enc.transform(X2)
    assert y2.shape == (len(X2), 50)


@pytest.mark.parametrize("input_type", ["numpy", "pandas"])
@pytest.mark.parametrize("missing", ["error", "zero_impute", "aaa"])
@pytest.mark.parametrize("hashing", ["fast", "murmur", "aaa"])
def test_missing_values(input_type: str, missing: str, hashing: str) -> None:
    X = ["Red", np.nan, "green", "blue", "green", "green", "blue", float("nan")]
    n = 3
    z = np.zeros(n)

    if input_type == "numpy":
        X = np.array(X, dtype=object)[:, None]
    elif input_type == "pandas":
        X = pd.DataFrame(X)

    encoder = MinHashEncoder(
        n_components=n, hashing=hashing, minmax_hash=False, handle_missing=missing
    )

    if hashing == "aaa":
        with pytest.raises(ValueError, match=r"Got hashing="):
            encoder.fit_transform(X)
    else:
        if missing == "error":
            if input_type in ["numpy", "pandas"]:
                with pytest.raises(
                    ValueError, match=r"Found missing values in input data; set"
                ):
                    encoder.fit_transform(X)
        elif missing == "zero_impute":
            y = encoder.fit_transform(X)
            assert np.array_equal(y[1], z)
            assert np.array_equal(y[-1], z)
        else:
            with pytest.raises(ValueError, match=r"Got handle_missing="):
                encoder.fit_transform(X)
    return


def test_missing_values_none() -> None:
    # Test that "None" is also understood as a missing value
    a = np.array([["a", "b", None, "c"]], dtype=object).T

    enc = MinHashEncoder()
    d = enc.fit_transform(a)
    assert_array_equal(d[2], 0)

    e = np.array([["a", "b", "", "c"]], dtype=object).T
    f = enc.fit_transform(e)
    assert_array_equal(f[2], 0)


def test_cache_overflow() -> None:
    # Regression test for cache overflow resulting in -1s in encoding
    def get_random_string(length):
        letters = ascii_lowercase
        result_str = "".join(random.choice(letters) for _ in range(length))
        return result_str

    encoder = MinHashEncoder(n_components=3)
    capacity = encoder._capacity
    raw_data = [get_random_string(10) for _ in range(capacity + 1)]
    raw_data = np.array(raw_data)[:, None]
    y = encoder.fit_transform(raw_data)

    assert len(y[y == -1.0]) == 0


@skip_if_no_parallel
def test_parallelism() -> None:
    # Test that parallelism works
    encoder = MinHashEncoder(n_components=3, n_jobs=1)
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]
    y = encoder.fit_transform(X)
    for n_jobs in [None, 2, -1]:
        encoder = MinHashEncoder(n_components=3, n_jobs=n_jobs)
        y_parallel = encoder.fit_transform(X)
        assert_array_equal(y, y_parallel)

    # Test with threading backend
    encoder = MinHashEncoder(n_components=3, n_jobs=2)
    with joblib.parallel_backend("threading"):
        y_threading = encoder.fit_transform(X)
    assert_array_equal(y, y_threading)
    assert encoder.n_jobs == 2


DEFAULT_JOBLIB_BACKEND = joblib.parallel.get_active_backend()[0].__class__


class DummyBackend(DEFAULT_JOBLIB_BACKEND):  # type: ignore
    """
    A dummy backend used to check that specifying a backend works
    in MinHashEncoder.
    The `count` attribute is used to check that the backend is used.
    Copied from https://github.com/scikit-learn/scikit-learn/blob/36958fb240fbe435673a9e3c52e769f01f36bec0/sklearn/ensemble/tests/test_forest.py  # noqa
    """

    def __init__(self, *args, **kwargs):
        self.count = 0
        super().__init__(*args, **kwargs)

    def start_call(self):
        self.count += 1
        return super().start_call()


joblib.register_parallel_backend("testing", DummyBackend)


@skip_if_no_parallel
def test_backend_respected() -> None:
    """
    Test that the joblib backend is used.
    Copied from https://github.com/scikit-learn/scikit-learn/blob/36958fb240fbe435673a9e3c52e769f01f36bec0/sklearn/ensemble/tests/test_forest.py  # noqa
    """
    # Test that parallelism works
    encoder = MinHashEncoder(n_components=3, n_jobs=2)
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]

    with joblib.parallel_backend("testing") as (ba, n_jobs):
        encoder.fit_transform(X)

    assert ba.count > 0


def test_correct_arguments() -> None:
    # Test that the correct arguments are passed to the hashing function
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]
    # Write an incorrect value for the `hashing` argument
    with pytest.raises(ValueError, match=r"expected any of"):
        encoder = MinHashEncoder(n_components=3, hashing="incorrect")
        encoder.fit_transform(X)

    # Write an incorrect value for the `handle_missing` argument
    with pytest.raises(ValueError, match=r"expected any of"):
        encoder = MinHashEncoder(n_components=3, handle_missing="incorrect")
        encoder.fit_transform(X)

    # Use minmax_hash with murmur hashing
    with pytest.raises(ValueError, match=r"minmax_hash encoding is not supported"):
        encoder = MinHashEncoder(n_components=2, minmax_hash=True, hashing="murmur")
        encoder.fit_transform(X)

    # Use minmax_hash with an odd number of components
    with pytest.raises(ValueError, match=r"n_components should be even"):
        encoder = MinHashEncoder(n_components=3, minmax_hash=True)
        encoder.fit_transform(X)


def test_check_fitted_minhash_encoder() -> None:
    """Test that calling transform before fit raises an error"""
    encoder = MinHashEncoder(n_components=3)
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]
    with pytest.raises(NotFittedError):
        encoder.transform(X)

    # Check that it works after fitting
    encoder.fit(X)
    encoder.transform(X)


def test_deterministic():
    """Test that the encoder is deterministic"""
    # TODO: add random state to encoder
    encoder1 = MinHashEncoder(n_components=4)
    encoder2 = MinHashEncoder(n_components=4)
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]
    encoded1 = encoder1.fit_transform(X)
    encoded2 = encoder2.fit_transform(X)
    assert_array_equal(encoded1, encoded2)


def test_get_feature_names_out():
    """Test that get_feature_names_out returns the correct feature names"""
    encoder = MinHashEncoder(n_components=4)
    X = pd.DataFrame(
        {
            "col1": ["a", "b", "c", "d", "e", "f", "g", "h"],
            "col2": ["a", "b", "c", "d", "e", "f", "g", "h"],
        }
    )
    encoder.fit(X)
    expected_columns = np.array(
        ["col1_0", "col1_1", "col1_2", "col1_3", "col2_0", "col2_1", "col2_2", "col2_3"]
    )
    assert_array_equal(np.array(encoder.get_feature_names_out()), expected_columns)

    # Test that it works with a list of strings
    encoder = MinHashEncoder(n_components=4)
    X = np.array(["a", "b", "c", "d", "e", "f", "g", "h"])[:, None]
    encoder.fit(X)
    expected_columns = np.array(["x0_0", "x0_1", "x0_2", "x0_3"])
    assert_array_equal(np.array(encoder.get_feature_names_out()), expected_columns)


def test_merge_transformers() -> None:
    # check that fitting on each column separately and then merging the
    # transformers gives the same result as fitting on the whole dataset

    # generate data
    X = np.concatenate([generate_data(100, random_state=i) for i in range(3)], axis=1)
    X = pd.DataFrame(X, columns=["col0", "col1", "col2"])

    # fit on each column separately
    enc_list = []
    for i in range(3):
        enc = MinHashEncoder()
        enc.fit(X[[f"col{i}"]])
        enc_list.append(enc)
    enc_merged = MinHashEncoder._merge(enc_list)

    # fit on the whole dataset
    enc = MinHashEncoder()
    enc.fit(X)

    # check that the results are the same
    # check transform
    assert_array_equal(enc_merged.transform(X), enc.transform(X))
    # check get_feature_names_out
    # assert enc_merged.get_feature_names_out() == enc.get_feature_names_out()
    # check that the hash_dict_ attribute is the same
    assert enc.hash_dict_.cache.keys() == enc_merged.hash_dict_.cache.keys()
    for key in enc.hash_dict_.cache.keys():
        assert_array_equal(enc.hash_dict_.cache[key], enc_merged.hash_dict_.cache[key])
    # check all attributes
    assert enc_merged._capacity == enc._capacity
    assert enc_merged.n_features_in_ == enc.n_features_in_
    # check feature_names_in_
    assert_array_equal(enc_merged.feature_names_in_, enc.feature_names_in_)


def test_split_transformers() -> None:
    # check that splitting the transformer after fitting
    # doesn't change the output of transform

    # generate data
    X = np.concatenate([generate_data(100, random_state=i) for i in range(3)], axis=1)
    X = pd.DataFrame(X, columns=["col0", "col1", "col2"])

    # fit on the whole dataset
    enc = MinHashEncoder()
    enc.fit_transform(X)

    # split the transformer
    enc_list = copy.deepcopy(enc)._split()

    # fit on each column separately
    index = 0
    for i in range(3):
        # check that the results are the same
        # check transform
        transformed_X_i = enc_list[i].transform(X[[f"col{i}"]])
        assert_array_equal(
            transformed_X_i,
            enc.transform(X)[:, index : index + transformed_X_i.shape[1]],
        )
        # check get_feature_names_out
        assert_array_equal(
            np.array(enc_list[i].get_feature_names_out()),
            np.array(enc.get_feature_names_out())[
                index : index + transformed_X_i.shape[1]
            ],
        )
        # check self.feature_names_in_
        assert enc_list[i].feature_names_in_ == [f"col{i}"]
        # check self.n_features_in_
        assert enc_list[i].n_features_in_ == 1
        index += transformed_X_i.shape[1]
        # check all attributes
        assert enc_list[i]._capacity == enc._capacity
        # check hash_dict_
        # TODO: do we want the hash_dict_ to be the same?
        assert enc.hash_dict_.cache.keys() == enc_list[i].hash_dict_.cache.keys()
        for key in enc.hash_dict_.cache.keys():
            assert_array_equal(
                enc.hash_dict_.cache[key], enc_list[i].hash_dict_.cache[key]
            )


def test_split_and_merge_transformers() -> None:
    # check that splitting the transformer after fitting
    # and then merging the transformers doesn't change the result

    # generate data
    X = np.concatenate([generate_data(100, random_state=i) for i in range(3)], axis=1)
    X = pd.DataFrame(X, columns=["col0", "col1", "col2"])

    # fit on the whole dataset
    enc = MinHashEncoder()
    enc.fit(X)

    # split the transformer
    enc_list = copy.deepcopy(enc)._split()

    # merge the transformers
    enc_merged = MinHashEncoder._merge(enc_list)

    # check that the results are the same
    # check transform
    assert_array_equal(enc_merged.transform(X), enc.transform(X))
    # check get_feature_names_out
    assert enc_merged.get_feature_names_out() == enc.get_feature_names_out()
    # check hash_dict_
    assert enc.hash_dict_.cache.keys() == enc_merged.hash_dict_.cache.keys()
    for key in enc.hash_dict_.cache.keys():
        assert_array_equal(enc.hash_dict_.cache[key], enc_merged.hash_dict_.cache[key])
    # check all attributes
    assert enc_merged._capacity == enc._capacity
    assert enc_merged.n_features_in_ == enc.n_features_in_
    # check feature_names_in_
    assert_array_equal(enc_merged.feature_names_in_, enc.feature_names_in_)
