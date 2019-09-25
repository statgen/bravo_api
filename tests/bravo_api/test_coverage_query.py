import pytest


def test_noargs_query(client, config):
   response = client.get('/coverage')
   assert response.status_code == 422
   payload = response.get_json()
   assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
   assert payload['data'] is None
   assert payload['total'] is None
   assert payload['limit'] is None
   assert payload['next'] is None
   assert payload['error'] is not None and len(payload['error']) > 0


def test_minargs_small_query(client, config):
   chrom = 22
   start = 50673415
   stop = 50673515
   response = client.get(f'/coverage?chrom={chrom}&start={start}&stop={stop}')
   assert response.status_code == 200
   payload = response.get_json()
   assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
   assert payload['data'] is not None and len(payload['data']) == stop - start + 1
   assert payload['total'] is not None and payload['total'] == len(payload['data'])
   assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
   assert payload['next'] is None
   assert payload['error'] is None
   # check if no binning
   for item in payload['data']:
      assert item['start'] == item['end']


def test_minargs_large_query(client, config):
   chrom = 22
   start = 25016233
   stop = 25267187
   response = client.get(f'/coverage?chrom={chrom}&start={start}&stop={stop}')
   assert response.status_code == 200
   payload = response.get_json()
   assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
   assert payload['data'] is not None and len(payload['data']) < stop - start + 1
   assert payload['total'] is not None and payload['total'] == len(payload['data'])
   assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
   assert payload['next'] is None
   assert payload['error'] is None


def test_limit_too_high_query(client, config):
   chrom = 22
   start = 25016233
   stop = 25267187
   response = client.get(f'/coverage?chrom={chrom}&start={start}&stop={stop}&limit={config["BRAVO_API_PAGE_LIMIT"] + 1}')
   assert response.status_code == 422
   payload = response.get_json()
   assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
   assert payload['data'] is None
   assert payload['total'] is None
   assert payload['limit'] is None
   assert payload['next'] is None
   assert payload['error'] is not None and len(payload['error']) > 0


def test_paged_large_query(client, config):
   chrom = 22
   start = 25016233
   stop = 25267187
   response = client.get(f'/coverage?chrom={chrom}&start={start}&stop={stop}')
   all_data = response.get_json()['data']

   next_link = f'/coverage?chrom={chrom}&start={start}&stop={stop}&limit=1000'
   paged_data = []
   while next_link is not None:
      response = client.get(next_link)
      assert response.status_code == 200, response.get_json()
      payload = response.get_json()
      assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
      assert payload['data'] is not None and len(payload['data']) <= 1000
      assert payload['total'] is not None and payload['total'] == len(all_data)
      assert payload['limit'] is not None and payload['limit'] == 1000
      assert payload['error'] is None
      paged_data.extend(payload['data'])
      next_link = payload['next']
   assert all_data == paged_data
