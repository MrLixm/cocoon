__all__ = (
    "numpy_array2string_oneline",
    "simplify",
    "split_at_words",
    "lru_cache",
)

import functools
import re
from copy import deepcopy

import unicodedata
from typing import Any

import numpy


def simplify(object_: Any, allow_unicode: bool = False) -> str:
    """
    Generate a more simple string representation fo the given object.

    Convert to ASCII if ``allow_unicode`` is *False*.

    Args:
        object_:
            Object to convert to a slug.
        allow_unicode:
            Whether to allow unicode characters in the generated slug.

    Returns:
        Generated slug.

    References:
        - [1] inspired from Django Software Foundation ``slugify()``
    """

    value = str(object_)

    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    value = value.lower()
    value = re.sub(r"[\s\\/'\"]+", "-", value)
    value = re.sub(r"[()\[\]{}]", "", value)
    value = re.sub(r"-{2,}", "--", value)
    return value


def split_at_words(source_str: str, split_camel_case: bool = False) -> list[str]:
    """
    Split the given string into multiple words using commonly used delimiter characters.

    Example::

        >>> source = "5D Mark II - Spac-o-ween - XS - 001"
        >>> result = split_at_words(source)
        ["5D", "Mark", "II", "Spac", "o", "ween", "XS", "001"]

        >>> source = "A009C002_190210_R0EI_Alexa_LogCWideGamut"
        >>> result = split_at_words(source, split_camel_case=True)
        ["A009C002", "190210", "R0EI", "Alexa", "Log", "C", "Wide", "Gamut"]


    Args:
        source_str:
        split_camel_case:
            If True, consider camelcase string like a group of word and
            split at each uppercase letter.

    Returns:
        list of string white the word delimiter removed.
    """

    if split_camel_case:
        splitted = re.sub(
            r"([A-Z][a-z]+)|[._-]",
            r" \1",
            re.sub(
                r"([A-Z0-9]+)",
                r" \1",
                source_str,
            ),
        ).split()

    else:
        splitted = re.sub(r"[._-]", r" ", source_str).split()

    return splitted


def numpy_array2string_oneline(array: numpy.ndarray) -> str:
    """
    Convert the given numpy array to a one line readable string.
    """
    return numpy.array2string(array, separator=",").replace("\n", "")


def lru_cache(maxsize=128, typed=False, copy=False):
    """
    Same as functools.lru_cache but can return unique instances.

    Args:
        maxsize:
            If is set to None, the LRU features are disabled and the cache can grow without bound.
        typed:
            If True, arguments of different types will be cached separately.
            For example, f(3.0) and f(3) will be treated as distinct calls with distinct results
        copy: If True return a deepcopy of the cached object

    References:
        - [1] https://stackoverflow.com/q/54909357/13806195
    """
    if not copy:
        return functools.lru_cache(maxsize, typed)

    def decorator(func):
        cached_func = functools.lru_cache(maxsize, typed)(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return deepcopy(cached_func(*args, **kwargs))

        return wrapper

    return decorator
