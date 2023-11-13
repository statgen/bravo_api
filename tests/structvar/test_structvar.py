from bravo_api.blueprints.structvar import structvar
from flask import Flask

app = Flask('dummy')
app.register_blueprint(structvar.bp)

# See mongo_fixtures/strucvar.json for structvar collection fixture values


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


def test_structvar_multiple_results(mocker, mongodb):
    result = structvar.sv_region(mongodb.structvar, "3", roi_start=950000, roi_stop=1400000)
    assert isinstance(result, list)
    assert len(result) == 3
