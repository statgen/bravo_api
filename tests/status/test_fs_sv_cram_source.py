from bravo_api.blueprints.structvar import FsSvCramSource


def test_extract_pos_vals():
    sv_id = "DUP_20:5001000-5002000"
    result = FsSvCramSource.extract_pos_vals(sv_id)

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == "chr20"
    assert result[1] == 5001000
    assert result[2] == 5002000
