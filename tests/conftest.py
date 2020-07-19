import pytest
from pytest import Session
from pytest import Item

from epi_code_generator.symbol import EpiSymbol

from typing import List


def pytest_configure(config):

    config.addinivalue_line(
        "markers", "order(int): mark test to specify relative order"
    )

def pytest_assertrepr_compare(op, left, right):

    if isinstance(left, EpiSymbol) and isinstance(right, EpiSymbol) and op == "==":

        import difflib

        diffs = [diff for diff in difflib.ndiff(repr(left).splitlines(keepends=False), repr(right).splitlines(keepends=False)) if diff[0] != ' ']
        if len(diffs) != 0:

            diffs.insert(0, f'Difference between {left.name} and {right.name}')
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
