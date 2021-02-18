# Search redirects to appropriate endpoint
def test_search(client, config):
    response = client.get('/search?value=20%3A250000-250100')
    assert response.status_code == 302
