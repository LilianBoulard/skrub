import random

import numpy as np
from numpy.typing import NDArray


def generate_data(
    n_samples: int,
    as_list: bool = False,
    random_state: int | float | str | bytes | bytearray | None = None,
    sample_length: int = 100,
) -> NDArray:
    if random_state is not None:
        random.seed(random_state)
    MAX_LIMIT = 255  # extended ASCII Character set
    str_list = []
    for i in range(n_samples):
        random_string = "category "
        for _ in range(sample_length):
            random_integer = random.randint(1, MAX_LIMIT)
            random_string += chr(random_integer)
            if random_integer < 50:
                random_string += "  "
        str_list += [random_string]
    if as_list is True:
        X = str_list
    else:
        X = np.array(str_list).reshape(n_samples, 1)
    return X


def is_valid_attribute(attribute):
    # check that the type is not too weird
    # so we can check equality
    valid_types = (
        int,
        float,
        np.ndarray,
        str,
        bool,
        type(None),
        list,
        tuple,
        dict,
        set,
    )

    if isinstance(attribute, (list, tuple, set)):
        return all(is_valid_attribute(item) for item in attribute)
    elif isinstance(attribute, dict):
        return all(
            is_valid_attribute(key) and is_valid_attribute(value)
            for key, value in attribute.items()
        )
    else:
        return isinstance(attribute, valid_types)


def transformers_equal(transformer1, transformer2):
    # Check if the transformers are of the same type
    if type(transformer1) != type(transformer2):
        return False

    # if string transformers, check if they are the same
    if isinstance(transformer1, str):
        return transformer1 == transformer2

    # Compare hyperparameters
    if transformer1.get_params() != transformer2.get_params():
        return False

    # Compare fitted attributes
    for attribute in transformer1.__dict__:
        if attribute.endswith("_"):
            if not is_valid_attribute(getattr(transformer1, attribute)):
                # check that the type is the same
                if not isinstance(
                    getattr(transformer1, attribute),
                    type(getattr(transformer2, attribute)),
                ):
                    return False
            else:
                if not np.array_equal(
                    getattr(transformer1, attribute), getattr(transformer2, attribute)
                ):
                    return False

    return True


def transformers_list_equal(transformers_list1, transformers_list2):
    # check equaility for list of 3-tuples (name, transformer, columns)
    # used in the TableVectorizer
    if len(transformers_list1) != len(transformers_list2):
        return False
    for (name1, transformer1, columns1), (name2, transformer2, columns2) in zip(
        transformers_list1, transformers_list2
    ):
        if name1 != name2:
            return False
        if columns1 != columns2:
            return False
        if not transformers_equal(transformer1, transformer2):
            return False
    return True
