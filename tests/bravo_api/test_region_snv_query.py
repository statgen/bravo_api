import pytest
from bravo_api.models.readers import snv_lof2code, snv_consequence2code

import sys


#@pytest.mark.skip
def test_noargs_query(client, config):
    response = client.get('/region/snv')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_minargs_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == 17813
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None


#@pytest.mark.skip
def test_extraargs_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&iamextrakey=true')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_PASS_filter_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data = response.get_json()['data']

    passed = set()
    nonpassed = set()
    svm = set()
    disc_and_exhet = set()
    disc_or_exhet = set()
    for item in all_data:
        if 'PASS' in item['filter']:
            passed.add(item['variant_id'])
        else:
            nonpassed.add(item['variant_id'])
            if 'SVM' in item['filter']:
                svm.add(item['variant_id'])
            if 'DISC' in item['filter'] and 'EXHET' in item['filter']:
                disc_and_exhet.add(item['variant_id'])
            if 'DISC' in item['filter'] or 'EXHET' in item['filter']:
                disc_or_exhet.add(item['variant_id'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=eq:PASS')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(passed)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert passed == set(v['variant_id'] for v in payload['data'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=ne:PASS')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(nonpassed)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert nonpassed == set(v['variant_id'] for v in payload['data'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=SVM')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(svm)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert svm == set(v['variant_id'] for v in payload['data'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=eq:DISC,eq:EXHET')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(disc_and_exhet)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert disc_and_exhet == set(v['variant_id'] for v in payload['data'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=eq:DISC&filter=eq:EXHET')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(disc_or_exhet)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert disc_or_exhet == set(v['variant_id'] for v in payload['data'])


def test_af_filter_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    min_af = 0.05
    max_af = 0.1
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data = response.get_json()['data']

    max_af_variants = []
    min_af_variants = []
    min_max_af_variants = []

    for item in all_data:
        if item['allele_freq'] <= max_af:
            max_af_variants.append(item['variant_id'])
        if item['allele_freq'] > min_af:
            min_af_variants.append(item['variant_id'])
        if item['allele_freq'] > min_af and item['allele_freq'] <= max_af:
            min_max_af_variants.append(item['variant_id'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&allele_freq=lte:{max_af}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(max_af_variants)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert all(v1 == v2 for v1, v2 in zip(max_af_variants, (v['variant_id'] for v in payload['data'])))

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&allele_freq=gt:{min_af}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(min_af_variants)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert all(v1 == v2 for v1, v2 in zip(min_af_variants, (v['variant_id'] for v in payload['data'])))

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&allele_freq=gt:{min_af},lte:{max_af}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(min_max_af_variants)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert all(v1 == v2 for v1, v2 in zip(min_max_af_variants, (v['variant_id'] for v in payload['data'])))



#@pytest.mark.skip
def test_lof_filter_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data = response.get_json()['data']

    n = 0
    hc_lof = []
    lc_lof = []
    lof = []
    no_lof = []
    for item in all_data:
        if not 'PASS' in item['filter']:
            continue
        n += 1
        n_hc_lof = 0
        n_lc_lof = 0
        region_annotation = item['annotation']['region']
        n_hc_lof += sum(x == 'HC' for x in region_annotation.get('lof', []))
        n_lc_lof += sum(x == 'LC' for x in region_annotation.get('lof', []))
        if n_hc_lof > 0:
            hc_lof.append(item)
        if n_lc_lof > 0:
            lc_lof.append(item)
        if n_hc_lof > 0 or n_lc_lof > 0:
            lof.append(item)
        else:
            no_lof.append(item)

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=HC')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(hc_lof)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert hc_lof == payload['data']

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=LC')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(lc_lof)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert lc_lof == payload['data']

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=HC&annotation.region.lof=LC')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(lof)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert lof == payload['data']

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=ne:HC,ne:LC')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(no_lof)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert no_lof == payload['data']


#@pytest.mark.skip
def test_consequence_filter_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data = response.get_json()['data']

    n = 0
    splice_acceptor = set()
    missense = set()
    for item in all_data:
        n += 1
        n_splice_acceptor = 0
        n_missense = 0
        region_annotation = item['annotation']['region']
        n_splice_acceptor += 'splice_acceptor_variant' in region_annotation['consequence']
        n_missense += 'missense_variant' in region_annotation['consequence']
        if n_splice_acceptor > 0:
            splice_acceptor.add(item['variant_id'])
        if n_missense > 0:
            missense.add(item['variant_id'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&annotation.region.consequence=splice_acceptor_variant')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(splice_acceptor)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert splice_acceptor == set(v['variant_id'] for v in payload['data'])

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&annotation.region.consequence=missense_variant')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(missense)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    assert missense == set(v['variant_id'] for v in payload['data'])


#@pytest.mark.skip
def test_complex_filter_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=eq:PASS')
    assert response.status_code == 200
    all_data = response.get_json()['data']

    all_data_filtered = []
    for item in all_data:
        if 'frameshift_variant' in item['annotation']['region']['consequence'] and 'HC' in item['annotation']['region']['lof']:
            all_data_filtered.append(item)

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=eq:PASS&annotation.region.consequence=eq:frameshift_variant&annotation.region.lof=eq:HC')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_filtered)
    assert all_data_filtered == payload['data']


#@pytest.mark.skip
def test_hom_sort_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data_nosort = response.get_json()['data']

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=hom_count:desc')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_nosort)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    all_data_sorted = payload['data']
    assert sorted(all_data_nosort, key = lambda item: item['hom_count'], reverse = True) == all_data_sorted


#@pytest.mark.skip
def test_cadd_sort_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data_nosort = response.get_json()['data']

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=cadd_phred:desc')
    assert response.status_code == 200
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_nosort)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    all_data_sorted = payload['data']
    assert sorted(all_data_nosort, key = lambda item:  float("-inf") if item['cadd_phred'] is None else item['cadd_phred'], reverse = True) == all_data_sorted


#@pytest.mark.skip
def test_lof_sort_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data_nosort = response.get_json()['data']

    def get_weight(item):
        return sorted(set([ snv_lof2code[x] for x in item['annotation']['region'].get('lof',[]) ]), reverse = True)

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.lof:desc')
    assert response.status_code == 200, response.get_json()
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_nosort)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    all_data_sorted = payload['data']
    assert sorted(all_data_nosort, key = lambda item: get_weight(item), reverse = True) == all_data_sorted


#@pytest.mark.skip
def test_consequence_sort_query(client, config):
    chrom = 22
    start = 46151865
    stop = 46243776
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    all_data_nosort = response.get_json()['data']

    def get_weight(item):
        return sorted(set([ snv_consequence2code[x] for x in item['annotation']['region'].get('consequence',[]) ]), reverse = True)

    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.consequence:desc')
    assert response.status_code == 200, response.get_json()
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is not None and len(payload['data']) == len(all_data_nosort)
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is not None and payload['limit'] == config['BRAVO_API_PAGE_LIMIT']
    assert payload['next'] is None
    assert payload['error'] is None
    all_data_sorted = payload['data']

    assert sorted(all_data_nosort, key = lambda item: get_weight(item), reverse = True) == all_data_sorted


#@pytest.mark.skip
def test_limit_too_high_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&limit={config["BRAVO_API_PAGE_LIMIT"] + 1}')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


#@pytest.mark.skip
def test_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}')
    all_data = response.get_json()['data']
    page_size = 1000
    assert len(all_data) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&limit={page_size}'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200, response.get_json()
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(all_data)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert all_data == paged_data


#@pytest.mark.skip
def test_PASS_filter_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS')
    passed = response.get_json()['data']
    page_size = 100
    assert len(passed) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&limit={page_size}'
    paged_passed = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(passed)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_passed.extend(payload['data'])
        next_link = payload['next']
    assert passed == paged_passed


#@pytest.mark.skip
def test_af_filter_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&allele_freq=lte:0.01')
    max_af_variants = [ v['variant_id'] for v in response.get_json()['data'] ]
    page_size = 100
    assert len(max_af_variants) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&allele_freq=lte:0.01&limit={page_size}'
    paged_max_af_variants = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(max_af_variants)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_max_af_variants.extend(v['variant_id'] for v in payload['data'])
        next_link = payload['next']
    assert len(max_af_variants) == len(paged_max_af_variants)
    assert all(v1 == v2 for v1, v2 in zip(max_af_variants, paged_max_af_variants))


#@pytest.mark.skip
def test_LoF_filter_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=HC&annotation.region.lof=LC')
    passed_lof = response.get_json()['data']
    page_size = 2
    assert len(passed_lof) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.lof=HC&annotation.region.lof=LC&limit={page_size}'
    paged_passed_lof = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(passed_lof)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_passed_lof.extend(payload['data'])
        next_link = payload['next']
    assert passed_lof == paged_passed_lof


#@pytest.mark.skip
def test_consequence_filter_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.consequence=missense_variant')
    passed_missense = response.get_json()['data']
    page_size = 10
    assert len(passed_missense) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&annotation.region.consequence=missense_variant&limit={page_size}'
    paged_passed_missense = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(passed_missense)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_passed_missense.extend(payload['data'])
        next_link = payload['next']
    assert passed_missense == paged_passed_missense


#@pytest.mark.skip
def test_hom_sorted_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=hom_count:desc')
    all_data = response.get_json()['data']
    page_size = 100
    assert len(all_data) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=hom_count:desc&limit={page_size}'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(all_data)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert all_data == paged_data


#@pytest.mark.skip
def test_LoF_sorted_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.lof:desc')
    all_data = response.get_json()['data']
    page_size = 10
    assert len(all_data) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.lof:desc&limit={page_size}'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(all_data)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert all_data == paged_data


#@pytest.mark.skip
def test_consequence_sorted_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.consequence:desc')
    all_data = response.get_json()['data']
    page_size = 100
    assert len(all_data) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&sort=annotation.region.consequence:desc&limit={page_size}'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(all_data)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert all_data == paged_data


#@pytest.mark.skip
def test_rsid_sorted_paged_query(client, config):
    chrom = 22
    start = 50673415
    stop = 50734298
    rsid = 'rs5'
    response = client.get(f'/region/snv?chrom={chrom}&start={start}&stop={stop}&rsids=like:{rsid}&sort=annotation.region.consequence:desc')
    all_data = response.get_json()['data']
    page_size = 100
    assert len(all_data) > page_size
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&rsids=like:{rsid}&sort=annotation.region.consequence:desc&limit={page_size}'
    paged_data = []
    while next_link is not None:
        response = client.get(next_link)
        assert response.status_code == 200
        payload = response.get_json()
        assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
        assert payload['data'] is not None and len(payload['data']) <= page_size
        assert payload['total'] is not None and payload['total'] == len(all_data)
        assert payload['limit'] is not None and payload['limit'] == page_size
        assert payload['error'] is None
        paged_data.extend(payload['data'])
        next_link = payload['next']
    assert all_data == paged_data


#@pytest.mark.skip
def test_snv_histogram_query(client, config):
    chrom = 22
    start = 25016233
    stop = 25267187
    page_size = 10000
    windows = 1000
    next_link = f'/region/snv?chrom={chrom}&start={start}&stop={stop}&filter=PASS&limit={page_size}'
    all_data = 0
    while next_link is not None:
        response = client.get(next_link)
        all_data += len(response.get_json()['data'])
        next_link = response.get_json()['next']
    response = client.get(f'/region/snv/histogram?chrom={chrom}&start={start}&stop={stop}&filter=PASS&windows={windows}')
    assert response.status_code == 200
    payload = response.get_json()
    assert all( x in payload['data'] for x in ['chrom', 'window-size', 'windows'])
    assert len(payload['data']['windows']) > 0
    assert len(payload['data']['windows']) < windows
    assert all_data == sum(entry['count'] for entry in payload['data']['windows'])


#@pytest.mark.skip
def test_snv_summary_query(client, config):
    chrom = 22
    start = 25016233
    stop = 25267187
    response = client.get(f'/region/snv/summary?chrom={chrom}&start={start}&stop={stop}')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['data'] is not None
    assert payload['data']['all']['total'] == payload['data']['passed']['total'] + payload['data']['failed']['total']
    assert payload['data']['all']['total'] == payload['data']['all']['snv'] + payload['data']['all']['indels']
    assert payload['data']['passed']['total'] == payload['data']['passed']['snv'] + payload['data']['passed']['indels']
    assert payload['data']['failed']['total'] == payload['data']['failed']['snv'] + payload['data']['failed']['indels']
    assert payload['total'] is not None and payload['total'] == len(payload['data'])
    assert payload['limit'] is None
    assert payload['error'] is None
