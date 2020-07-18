from epi_code_generator.symbol import EpiSymbol


def pytest_assertrepr_compare(op, left, right):

    if isinstance(left, EpiSymbol) and isinstance(right, EpiSymbol) and op == "==":

        import difflib

        diffs = [diff for diff in difflib.ndiff(repr(left).splitlines(keepends=False), repr(right).splitlines(keepends=False)) if diff[0] != ' ']
        if len(diffs) != 0:

            diffs.insert(0, f'Difference between {left.name} and {right.name}')
            return diffs