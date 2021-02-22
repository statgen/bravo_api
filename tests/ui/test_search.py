# Search redirects to appropriate endpoint
def test_search(client, config):
    data = {'value': 'chr77:50000-50100'}
    response = client.get('/search', query_string=data)
    assert response.status_code == 302
