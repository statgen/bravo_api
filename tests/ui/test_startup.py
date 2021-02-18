# Smoke test to ensure __init__ runs
def test_root(client, config):
    response = client.get('/')
    assert response.status_code == 200
