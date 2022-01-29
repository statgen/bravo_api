from bravo_api.blueprints.legacy_ui import pretty_api


def test_munging_ui_sort_allowed_keys():
    ui_sort = [{'field': 'variant_id', 'dir': 'asc'}]
    result = pretty_api.munge_ui_sort(ui_sort)

    expected_result = [('variant_id', 'asc')]

    assert(expected_result == result)


def test_munging_ui_sort_not_allowed_keys():
    ui_sort = [{'field': 'foo', 'dir': 'asc'}]
    result = pretty_api.munge_ui_sort(ui_sort)

    expected_result = []

    assert(expected_result == result)


def test_munging_ui_sort_not_allowed_direction():
    ui_sort = [{'field': 'variant_id', 'dir': 'bad'}]
    result = pretty_api.munge_ui_sort(ui_sort)

    expected_result = []

    assert(expected_result == result)


def test_munging_ui_sort_directions():
    asc_sort = [{'field': 'rsids', 'dir': 'asc'},
                {'field': 'rsids', 'dir': 1},
                {'field': 'rsids', 'dir': ''},
                {'field': 'rsids', 'dir': None}]
    desc_sort = [{'field': 'rsids', 'dir': 'desc'},
                 {'field': 'rsids', 'dir': -1}]
    ui_sort = [*asc_sort, *desc_sort]

    result = pretty_api.munge_ui_sort(ui_sort)

    expected_result = [('rsids', 'asc'), ('rsids', 'asc'), ('rsids', 'asc'), ('rsids', 'asc'),
                       ('rsids', 'desc'), ('rsids', 'desc')]

    assert(expected_result == result)


def test_munging_ui_sort_mix_allowed_and_disallowed():
    bad_sort = [{'field': 'bad', 'dir': 'asc'},
                {'field': 'variant_id', 'dir': 'bad'},
                {'field': 'bad', 'dir': 'bad'}]
    good_sort = [{'field': 'pos', 'dir': 'asc'},
                 {'field': 'variant_id'},
                 {'field': 'allele_num', 'dir': 'desc'}]
    ui_sort = [*bad_sort, *good_sort]

    result = pretty_api.munge_ui_sort(ui_sort)

    expected_result = [('pos', 'asc'),
                       ('variant_id', 'asc'),
                       ('allele_num', 'desc')]

    assert(expected_result == result)
