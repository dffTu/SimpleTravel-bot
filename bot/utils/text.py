from fuzzywuzzy import fuzz
from typing import Union


def get_text_ratio(a: Union[None, str], b: str):
    if a is None:
        return 100
    partial_ratio = fuzz.partial_ratio(a, b)
    wratio = fuzz.WRatio(a, b)
    return max(partial_ratio, wratio)
