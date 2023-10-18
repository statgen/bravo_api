# import pymongo
from flask import current_app, Blueprint, jsonify, make_response
from flask_cors import CORS
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE
import logging


logger = logging.getLogger(__name__)
bp = Blueprint('eqtl', __name__)
CORS(bp)


class Parser(FlaskParser):
    # Override to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()


eqtl_argmap = {
    'gene': fields.Str(required=True, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}


@bp.route('/eqtl/susie', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_susie(args):
    result = susie(args['gene'])
    return make_response(jsonify(result))


@bp.route('/eqtl/cond', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_cond(args):
    result = cond(args['gene'])
    return make_response(jsonify(result))


def susie(gene_name):
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
    # if answer is None:
    #     return []
    # else:
    #     return answer['eqtls']
    return []


def cond(gene_name):
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
    # if answer is None:
    #     return []
    # else:
    #     return answer['eqtls']
    return []
