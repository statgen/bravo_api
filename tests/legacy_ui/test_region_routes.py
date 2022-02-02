from bravo_api.blueprints.legacy_ui import region_routes
from flask import Flask

app = Flask('dummy')
app.register_blueprint(region_routes.bp)
app.config['BRAVO_API_PAGE_LIMIT'] = 1000


def test_coverage_arg_passing(mocker):
    mock = mocker.patch('bravo_api.blueprints.legacy_ui.pretty_api.get_coverage',
                        side_effect={'foo': 100})
    # path args
    chrom = '11'
    start = 500000
    stop = 5001000
    # body args
    size = 100
    next = None

    with app.test_client() as client:
        client.post(f'/coverage/{chrom}-{start}-{stop}', json={'size': size, 'next': next})
    mock.assert_called_with(chrom, start, stop, size, 0)
