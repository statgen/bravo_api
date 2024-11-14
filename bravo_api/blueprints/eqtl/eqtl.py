from flask import current_app, Blueprint, jsonify, make_response, Response
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE
import logging


logger = logging.getLogger(__name__)
bp = Blueprint('eqtl', __name__)


class Parser(FlaskParser):
    # Override in order to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()


eqtl_argmap = {
    'gene': fields.Str(required=True, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}

ensg_argmap = {
    'ensembl': fields.Str(required=True, validate=lambda x: len(x) > 12 and len(x) < 17,
                          error_messages={
                              'validator_failed': 'String length must be between 13 and 16.'})
}


@bp.route('/eqtl/susie', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_susie(args: dict) -> Response:
    result = susie(args['gene'])
    return make_response(jsonify(result))


@bp.route('/eqtl/cond', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_cond(args: dict) -> Response:
    result = cond(args['gene'])
    return make_response(jsonify(result))


@bp.route('/eqtl/susie_count', methods=['GET'])
@parser.use_args(ensg_argmap, location='query')
def get_susie_count(args: dict) -> Response:
    result = susie_count(args['ensembl'])
    return make_response(jsonify(result))


@bp.route('/eqtl/cond_count', methods=['GET'])
@parser.use_args(ensg_argmap, location='query')
def get_cond_count(args: dict) -> Response:
    result = cond_count(args['ensembl'])
    return make_response(jsonify(result))


def susie(gene_name: str) -> list:
    """ Lookup eqtl data from SuSie analysis.
    @param gene_name.  Short name of gene e.g. UBQLNL
    """
    # Remove _id to allow response to be json serializable
    pipeline = [
        {'$match': {'gene_name': gene_name}},
        {'$lookup': {'from': "eqtl_susie",
                     'localField': "gene_id",
                     'foreignField': "phenotype_id",
                     'as': "eqtls"}},
        {'$project': {'_id': False, 'eqtls._id': False}}
    ]

    cursor = current_app.mmongo.db.genes.aggregate(pipeline)
    cursor.limit = 1
    answer = next(cursor, None)
    if answer is None:
        return []
    else:
        return answer['eqtls']


def cond(gene_name: str) -> list:
    # Remove _id to allow response to be json serializable
    pipeline = [
        {'$match': {'gene_name': gene_name}},
        {'$lookup': {'from': "eqtl_cond",
                     'localField': "gene_id",
                     'foreignField': "phenotype_id",
                     'as': "eqtls"}},
        {'$project': {'_id': False, 'eqtls._id': False}}
    ]

    cursor = current_app.mmongo.db.genes.aggregate(pipeline)
    cursor.limit = 1
    answer = next(cursor, None)
    if answer is None:
        return []
    else:
        return answer['eqtls']


def susie_count(ensembl_id: str) -> int:
    mongo_filter = {'phenotype_id': ensembl_id}
    result = current_app.mmongo.db.eqtl_susie.count_documents(mongo_filter)
    return result


def cond_count(ensembl_id: str) -> int:
    mongo_filter = {'phenotype_id': ensembl_id}
    result = current_app.mmongo.db.eqtl_cond.count_documents(mongo_filter)
    return result
