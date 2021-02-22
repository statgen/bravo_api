import pytest


@pytest.mark.integration
def test_noargs_query(client, config):
    response = client.get('/qc')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) > 0
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


@pytest.mark.integration
def test_name_query(client, config):
    response = client.get('/qc?name=STZ')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 1
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


@pytest.mark.integration
def test_bad_name_query(client, config):
    response = client.get('/qc?name=badname')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 0
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None
