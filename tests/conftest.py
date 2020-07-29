import pytest
from pytest import Session
from pytest import Item

from epigen.symbol import EpiSymbol

from typing import List


def pytest_configure(config):

    config.addinivalue_line(
        "markers", "order(int): mark test to specify relative order"
    )

def pytest_assertrepr_compare(op, left, right):

    if isinstance(left, EpiSymbol) and isinstance(right, EpiSymbol) and op == "==":
        repr_left = repr(left)
        repr_right = repr(right)

    elif isinstance(left, str) and isinstance(right, str) and op == "==":
        repr_left = left
        repr_right = right

    else:
        return None

    import difflib

    ndiffs = difflib.ndiff(repr_left.splitlines(keepends=False), repr_right.splitlines(keepends=False))
    diffs = [diff for diff in ndiffs if diff[0] != ' ']

    return diffs

def pytest_collection_modifyitems(session: Session, config, items: List[Item]):

    def cmp_order(x: Item, y: Item) -> int:

        xorder = x.get_closest_marker('order')
        if xorder is None:
            return 1

        yorder = y.get_closest_marker('order')
        if yorder is None:
            return -1

        return yorder.args[0] - xorder.args[0]

    import functools
    items.sort(key=functools.cmp_to_key(cmp_order), reverse=True)
