import pytest


def test_noargs_query(client, config):
    response = client.get('/region/sv')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


def test_minargs_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 616
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None


def test_extraargs_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&iamextrakey=true')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


def test_filter_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}')
    all_data_nofilter = response.get_json()['data']

    inversions = []
    noninversions = []
    inversions_or_deletions = []
    for item in all_data_nofilter:
        if item['type'] == 'Inversion':
            inversions.append(item)
            inversions_or_deletions.append(item)
        else:
            if item['type'] == 'Deletion':
                inversions_or_deletions.append(item)
            noninversions.append(item)

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=eq:Inversion')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(inversions)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert inversions == payload['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=Inversion')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(inversions)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert inversions == payload['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=ne:Inversion')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(noninversions)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert noninversions == payload['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=Inversion&type=Deletion')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(inversions_or_deletions)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert inversions_or_deletions == payload['data']


def test_PASS_filter_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}')
    all_data = response.get_json()['data']

    passed = []
    nonpassed = []
    for item in all_data:
        if 'PASS' in item['filter']:
            passed.append(item)
        else:
            nonpassed.append(item)

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&filter=eq:PASS')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(passed)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert passed == payload['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&filter=ne:PASS')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(nonpassed)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert nonpassed == payload['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&filter=FAIL')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(nonpassed)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert nonpassed == payload['data']



def test_sort_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}')
    all_data_nosort = response.get_json()['data']

    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&sort=avglen:desc')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_nosort)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    all_data_sorted = payload['data']
    assert sorted(all_data_nosort, key = lambda item: item['avglen'], reverse = True) == all_data_sorted


def test_limit_too_high_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&sort=avglen:desc&limit={config["BRAVO_API_PAGE_LIMIT"] + 1}')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


def test_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}')
    all_data = response.get_json()['data']

    next_link = f'/region/sv?chrom={chrom}&start={start}&stop={stop}&limit=100'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= 100
        assert payload['total'] is not None and payload['total'] == 616
        assert payload['limit'] is not None and payload['limit'] == 100
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert len(all_data) == len(paged_data)
    assert all_data == paged_data


def test_filtered_paged_query(client, config):
    print("test_filtered_paged_query")
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=Inversion')
    inversions = response.get_json()['data']

    next_link = f'/region/sv?chrom={chrom}&start={start}&stop={stop}&type=Inversion&limit=10'
    paged_inversions = []
    while next_link is not None:
        print(next_link)
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= 10
        assert payload['total'] is not None and payload['total'] == len(inversions)
        assert payload['limit'] is not None and payload['limit'] == 10
        assert payload['error'] is None
        paged_inversions.extend(payload['data'])
        next_link = payload['next']
    assert len(inversions) == len(paged_inversions)
    assert inversions == paged_inversions


def test_sorted_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/sv?chrom={chrom}&start={start}&stop={stop}&sort=avglen:desc')
    all_data_sorted = response.get_json()['data']

    next_link = f'/region/sv?chrom={chrom}&start={start}&stop={stop}&sort=avglen:desc&limit=100'
    paged_data_sorted = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= 100
        assert payload['total'] is not None and payload['total'] == 616
        assert payload['limit'] is not None and payload['limit'] == 100
        assert payload['error'] is None
        paged_data_sorted.extend(payload['data'])
        next_link = payload['next']
    assert len(all_data_sorted) == len(paged_data_sorted)
    assert all_data_sorted == paged_data_sorted
