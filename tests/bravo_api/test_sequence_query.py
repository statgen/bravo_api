import pytest
import os
import re


def test_noargs_query(client, config):
    response = client.get('/sequence')
    assert response.status_code == 422
    payload = response.get_json()
    assert all(x in payload for x in ['data', 'total', 'limit', 'next', 'error'])
    assert payload['data'] is None
    assert payload['total'] is None
    assert payload['limit'] is None
    assert payload['next'] is None
    assert payload['error'] is not None and len(payload['error']) > 0


def test_cram_full_hom_query(client, config):
    variant = '22-23971765-A-G'
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-01.bam')
    received_cram = os.path.join(os.getcwd(), 'test_sequence.cram')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=1&heterozygous=0', headers = {})
    assert response.status_code == 206
    assert response.headers.get('Content-Type', '') == 'application/octet-stream'
    assert 'Content-Length' in response.headers
    assert 'Content-Range' in response.headers
    with open(received_cram, 'bw') as ifile:
        ifile.write(response.data)
    received_cram_size = os.path.getsize(received_cram)
    os.remove(received_cram)
    assert received_cram_size == int(response.headers['Content-Length'])
    assert received_cram_size == os.path.getsize(cached_cram)
    m = re.search(r'bytes (\d+)-(\d+)/(\d+)', response.headers['Content-Range'])
    assert m is not None
    assert int(m.group(1)) == 0
    assert int(m.group(2)) == received_cram_size - 1
    assert int(m.group(3)) == os.path.getsize(cached_cram)


def test_cram_full_het_query(client, config):
    variant = '22-23971765-A-G'
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-1.bam')
    received_cram = os.path.join(os.getcwd(), 'test_sequence.cram')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=1&heterozygous=1', headers = {})
    assert response.status_code == 206
    assert response.headers.get('Content-Type', '') == 'application/octet-stream'
    assert 'Content-Length' in response.headers
    assert 'Content-Range' in response.headers
    with open(received_cram, 'bw') as ifile:
        ifile.write(response.data)
    received_cram_size = os.path.getsize(received_cram)
    os.remove(received_cram)
    assert received_cram_size == int(response.headers['Content-Length'])
    assert received_cram_size == os.path.getsize(cached_cram)
    m = re.search(r'bytes (\d+)-(\d+)/(\d+)', response.headers['Content-Range'])
    assert m is not None
    assert int(m.group(1)) == 0
    assert int(m.group(2)) == received_cram_size - 1
    assert int(m.group(3)) == os.path.getsize(cached_cram)


def test_cram_partial1_query(client, config):
    variant = '22-23971765-A-G'
    query_range_start = 0
    query_range_stop = 120000
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-01.bam')
    received_cram = os.path.join(os.getcwd(), 'test_sequence.cram')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=1&heterozygous=0', headers = {'Range': f'bytes={query_range_start}-{query_range_stop}'})
    assert response.status_code == 206
    assert response.headers.get('Content-Type', '') == 'application/octet-stream'
    assert 'Content-Length' in response.headers
    assert 'Content-Range' in response.headers
    with open(received_cram, 'bw') as ifile:
        ifile.write(response.data)
    received_cram_size = os.path.getsize(received_cram)
    os.remove(received_cram)
    assert received_cram_size == int(response.headers['Content-Length'])
    assert received_cram_size == os.path.getsize(cached_cram)
    m = re.search(r'bytes (\d+)-(\d+)/(\d+)', response.headers['Content-Range'])
    assert m is not None
    assert int(m.group(1)) == query_range_start
    assert int(m.group(2)) == query_range_stop - 1
    assert int(m.group(3)) == os.path.getsize(cached_cram)


def test_cram_partial2_query(client, config):
    variant = '22-23971765-A-G'
    query_range_start = 95000
    query_range_stop = 110000
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-01.bam')
    received_cram = os.path.join(os.getcwd(), 'test_sequence.cram')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=1&heterozygous=0', headers = {'Range': f'bytes={query_range_start}-{query_range_stop}'})
    assert response.status_code == 206
    assert response.headers.get('Content-Type', '') == 'application/octet-stream'
    assert 'Content-Length' in response.headers
    assert 'Content-Range' in response.headers
    with open(received_cram, 'bw') as ifile:
        ifile.write(response.data)
    received_cram_size = os.path.getsize(received_cram)
    os.remove(received_cram)
    assert received_cram_size == int(response.headers['Content-Length'])
    m = re.search(r'bytes (\d+)-(\d+)/(\d+)', response.headers['Content-Range'])
    assert m is not None
    assert int(m.group(1)) == query_range_start
    assert int(m.group(2)) == query_range_stop - 1
    assert int(m.group(3)) == os.path.getsize(cached_cram)


def test_crai_query(client, config):
    variant = '22-23971765-A-G'
    cached_crai = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-01.bam.bai')
    received_crai = os.path.join(os.getcwd(), 'test_sequence.crai')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=1&heterozygous=0&index=1')
    assert response.status_code == 200
    assert response.headers.get('Content-Type', '') == 'application/octet-stream'
    assert 'Content-Length' in response.headers
    with open(received_crai, 'bw') as ifile:
        ifile.write(response.data)
    received_crai_size = os.path.getsize(received_crai)
    os.remove(received_crai)
    assert received_crai_size == int(response.headers['Content-Length'])
    assert received_crai_size == os.path.getsize(cached_crai)


def test_unavailable_sample_max_no_bad_query(client, config):
    variant = '22-23971765-A-G'
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-20.bam')
    cached_crai = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-20.bam.bai')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=20&heterozygous=1', headers = {})
    assert response.status_code == 500
    assert os.path.exists(cached_cram) is False
    assert os.path.exists(cached_crai) is False


def test_unavailable_sample_max_no_ok_query(client, config):
    variant = '22-23971765-A-G' # has 123 hets and 4 homs
    cached_cram = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-05.bam')
    cached_crai = os.path.join(config['SEQUENCES_CACHE_DIR'], f'chr{variant}-05.bam.bai')
    response = client.get(f'/sequence?variant_id={variant}&sample_no=5&heterozygous=0', headers = {})
    assert response.status_code == 500
    assert os.path.exists(cached_cram) is False
    assert os.path.exists(cached_crai) is False
