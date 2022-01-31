from bravo_api.blueprints.legacy_ui import gene_routes
from flask import Flask

app = Flask('dummy')
app.register_blueprint(gene_routes.bp)
app.config['BRAVO_API_PAGE_LIMIT'] = 1000


def mock_get_genes_by_name(name):
    return({'data': [1, 2, 3], 'total': 3, 'limit': None, 'next': None, 'error': None})


def test_genes_by_name(mocker, client):
    mock = mocker.patch('bravo_api.blueprints.legacy_ui.pretty_api.get_genes_by_name',
                        side_effect=mock_get_genes_by_name)
    name = 'foo'
    with app.test_client() as client:
        resp = client.get(f'/genes/api/{name}')

    mock.assert_called_with(name)
    assert(resp.content_type == 'application/json')
