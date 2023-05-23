__all__ = (
    "numpy_array2string_oneline",
    "simplify",
    "split_at_words",
)


import re
import unicodedata
from typing import Any, Optional, Literal
from typing import Sequence

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


def prettify_table_list(
    table_list: Sequence[Sequence],
    headers_titles: Optional[list[str]] = None,
    column_margins: int = 1,
    column_padding: int = 0,
    alignement: Literal["left", "center", "right"] = "center",
):
    """
    Convert a table represented as a list to a pretty string for printing.

    The table is defined as::

        table_list = [
            [row1-column1, row1-column2, ...],
            [row2-column1, row2-column2, ...],
            ...
        ]

    Examples::

        >>> prettify_table_list([['Foo', 'foo'], ['Barrrrrr','bar']], ['Name', 'Alias'])
        _______________________
        | Name     | Alias    |
        | -------- | -------- |
        | Foo      | foo      |
        | Barrrrrr | bar      |
        _______________________


    Args:
        table_list:
            list of list, of stringifiable objects like list[rows]
            The first row can be the table headers if ``headers_titles`` is None.
        headers_titles:
            title to give to each column of the table.
            Optional, can just be the first row in ``table_list``
        column_margins: spacing around each column. Include the header separator row.
        column_padding: spacing aroun each column. Exclude the header separator row.
        alignement: justify the text in which direction. "left", "center" or "right"

    Returns:
        table_list represented as string

    """

    if headers_titles and not len(table_list[0]) == len(headers_titles):
        raise ValueError(
            f"Headers list must have the same len as each the first table_list element "
            f": {len(table_list[0])} != {len(headers_titles)}"
        )

    table_list = list(table_list)
    column_separator = "|".center(1 + column_margins * 2, " ")

    if alignement == "left":
        str_adjust = str.ljust
    elif alignement == "center":
        str_adjust = str.center
    else:
        str_adjust = str.rjust

    if headers_titles:
        table_list.insert(0, headers_titles)

    table_len = [len(subitem) for item in table_list for subitem in item]
    maximum_length = max(table_len)
    maximum_length_padded = maximum_length + column_padding * 2

    table_list.insert(1, ["-" * maximum_length_padded] * len(table_list[0]))

    row_list = []

    for row_index, row_data in enumerate(table_list):
        if not row_index == 1:  # ignore header separator
            row_data = map(
                lambda obj: str_adjust(str(obj), maximum_length_padded, " "),
                row_data,
            )

        row_data = map(lambda obj: f"{obj}".ljust(maximum_length, " "), row_data)
        row_str = f"{column_separator}".join(row_data)
        row_str = row_str.center(len(row_str) + column_margins * 2, " ")
        row_list.append(f"|{row_str}|")

    row_list.insert(0, "_" * len(row_list[0]))
    row_list.append("_" * len(row_list[0]))

    return "\n".join(row_list)


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
