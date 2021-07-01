import pytest  # noqa

# Top level conftest to provide behavior of running only unmarked tests.
#   i.e. skip running 'integration' tests without explicitly asking for them (-m 'integration')
# Solution from https://stackoverflow.com/a/55921778


def pytest_collection_modifyitems(items, config):
    # add `default` marker to all unmarked items
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("default")
    # Provide default mark expression to run unmarked tests, unless -m expression is given on CLI.
    markexpr = config.getoption("markexpr", '')
    if not markexpr:
        markexpr = "False"
    config.option.markexpr = f"default or ({markexpr})"
