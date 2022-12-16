from bravo_api.blueprints.legacy_ui import region_routes
from flask import Flask

app = Flask('dummy')
app.register_blueprint(region_routes.bp)


def test_chunked_coverage_call(mocker):
    mock = mocker.patch('bravo_api.blueprints.legacy_ui.pretty_api.chunked_coverage',
                        return_value={'dummy': 100})
    # path args
    args = {'chrom': '11', 'start': 500000, 'stop': 5001000, 'continue_from': 0}

    with app.test_client() as client:
        client.post('/chunked-coverage', json=args)

    mock.assert_called_with(*list(args.values()))


def test_chunked_coverage_validation(mocker):
    mock = mocker.patch('bravo_api.blueprints.legacy_ui.pretty_api.chunked_coverage',
                        return_value={'dummy': 100})
    # Bad start, stop, and continue_from arguments
    bad_arg_sets = [
        {'chrom': '11', 'start': -10, 'stop': 50_000, 'continue_from': 0},
        {'chrom': '11', 'start': 40_000, 'stop': 30_000, 'continue_from': 0},
        {'chrom': '11', 'start': 40_000, 'stop': 50_000, 'continue_from': 50_000}]

    with app.test_client() as client:
        for args in bad_arg_sets:
            resp = client.post('/chunked-coverage', json=args)
            assert(resp.status_code == 422)

    assert(not mock.called)
