import pytest
from bravo_api.models.readers import snv_lof2code, snv_consequence2code

import sys


#@pytest.mark.skip
def test_noargs_query(client, config):
    response = client.get('/snv')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_bad_id_query(client, config):
    response = client.get('/snv?variant_id=very-bad-variant-id')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0



#@pytest.mark.skip
def test_chrom_only_query(client, config):
    chrom = 22
    response = client.get(f'/snv?chrom={chrom}')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_pos_only_query(client, config):
    pos = 50673422
    response = client.get(f'/snv?pos={pos}')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_id_query(client, config):
    variant_id = '22-50673422-C-T'
    response = client.get(f'/snv?variant_id={variant_id}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 1
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_rsid_query(client, config):
    variant_rsid = 'rs34747326'
    response = client.get(f'/snv?variant_id={variant_rsid}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 1
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_rsid_many_query(client, config):
    variant_rsid = 'rs34'
    response = client.get(f'/snv?variant_id={variant_rsid}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) >= 1 and len(payload['data']) <= 10
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_id_empty_query(client, config):
    variant_id = '22-1-C-T'
    response = client.get(f'/snv?variant_id={variant_id}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 0
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_biallelic_chrom_pos_query(client, config):
    chrom = '22'
    pos = 50673422
    response = client.get(f'/snv?chrom={chrom}&pos={pos}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 1
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_multiallelic_chrom_pos_query(client, config):
    chrom = '22'
    pos = 50673438
    response = client.get(f'/snv?chrom={chrom}&pos={pos}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 2
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_chrom_pos_empty_query(client, config):
    chrom = '22'
    pos = 1
    response = client.get(f'/snv?chrom={chrom}&pos={pos}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 0
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is None
