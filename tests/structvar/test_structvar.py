from bravo_api.blueprints.structvar import structvar
from flask import Flask

app = Flask('dummy')
app.register_blueprint(structvar.bp)

# See mongo_fixtures/strucvar.json for structvar collection fixture values


def test_sv_id_well_formed():
    well_formed_sv_ids = ["DUP_1:14000100-14000600",
                          "INV_3:2200000-3200000",
                          "DEL_5:3002000-4003600"]
    for id in well_formed_sv_ids:
        assert structvar.is_sv_id_well_formed(id) is True


def test_sv_id_mal_formed():
    malformed_sv_ids = ["DUP1:14000100-14000600",
                        "INV_chr3:2200000-3200000",
                        "DEL_5:3,002,000-4,003,600"]
    for id in malformed_sv_ids:
        assert structvar.is_sv_id_well_formed(id) is False


def test_valid_sv_id():
    valid_sv_ids = ["DUP_1:14000100-14000600",
                    "INV_3:2200000-3200000",
                    "DEL_5:3002000-4003600"]

    for id in valid_sv_ids:
        assert structvar.is_sv_id_valid(id) is True


def test_invalid_sv_id():
    """
    Verify bad sv type, bad chromosome, start > stop,
      and positions too large position fail validation
    """
    too_big = structvar.MAX_POS + 1
    invalid_sv_ids = ["BAD_1:14000100-14000600",
                      "INV_33:2200000-3200000",
                      "DEL_5:6000000-4003600",
                      f"DEL_5:{too_big}-4003600",
                      f"DEL_5:6000000-{too_big}"]

    for id in invalid_sv_ids:
        assert structvar.is_sv_id_valid(id) is False


def test_structvar_fully_within_roi(mongodb):
    result = structvar.sv_region(mongodb.structvar, "1", roi_start=718600, roi_stop=823600)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['pos'] == 718601


def test_structvar_only_start_in_roi(mongodb):
    result = structvar.sv_region(mongodb.structvar, "1", roi_start=718600, roi_stop=718700)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['pos'] == 718601


def test_structvar_not_in_roi(mongodb):
    result = structvar.sv_region(mongodb.structvar, "1", roi_start=600600, roi_stop=718600)
    assert isinstance(result, list)
    assert len(result) == 0


def test_structvar_spans_roi(mongodb):
    result = structvar.sv_region(mongodb.structvar, "1", roi_start=720000, roi_stop=820000)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['pos'] == 718601


def test_structvar_removes_objectid(mongodb):
    result = structvar.sv_region(mongodb.structvar, "1", roi_start=720000, roi_stop=820000)
    sv = result[0]
    print(sv.keys())
    assert '_id' not in sv.keys()


def test_structvar_multiple_results(mocker, mongodb):
    result = structvar.sv_region(mongodb.structvar, "3", roi_start=950000, roi_stop=1400000)
    assert isinstance(result, list)
    assert len(result) == 3
