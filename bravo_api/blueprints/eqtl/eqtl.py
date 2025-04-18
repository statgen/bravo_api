from flask import current_app, Blueprint, jsonify, make_response, Response
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE, validate
import logging


logger = logging.getLogger(__name__)
bp = Blueprint('eqtl', __name__)


class Parser(FlaskParser):
    # Override in order to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()


######################
# API Arguement Maps #
######################

eqtl_argmap = {
    'gene': fields.Str(required=True, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}

ensg_argmap = {
    'ensembl': fields.Str(required=True,
                          validate=lambda x: len(x) > 12 and len(x) < 17 and x.startswith("ENSG"),
                          error_messages={
                              'validator_failed': 'Expecting string starting with ENSG and \
                              length 13 to 16.'})
}

eqtl_cpra_argmap = {
    'cpra': fields.Str(required=True, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}

region_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1),
                        error_messages={'invalid_string': 'String must not be empty.'}),
    'start': fields.Int(required=True, validate=validate.Range(min=1),
                        error_messages={'invalid_value': 'Value must be greater than 0.'}),
    'stop': fields.Int(required=True, validate=validate.Range(min=1),
                       error_messages={'invalid_value': 'Value must be greater than 0.'})
}


##################
# API End Points #
##################

@bp.route('/eqtl/susie', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_susie(args: dict) -> Response:
    if args['gene'].startswith("ENSG"):
        result = susie_ensembl(args['gene'])
    else:
        result = susie(args['gene'])
    return make_response(jsonify(result))


@bp.route('/eqtl/susie_count', methods=['GET'])
@parser.use_args(ensg_argmap, location='query')
def get_susie_count(args: dict) -> Response:
    result = susie_count(args['ensembl'])
    return make_response(jsonify(result))


@bp.route('/eqtl/susie_by_id', methods=['GET'])
@parser.use_args(eqtl_cpra_argmap, location='query')
def get_susie_by_id(args: dict) -> Response:
    result = susie_by_id(args['cpra'])
    return make_response(jsonify(result))


@bp.route('/eqtl/region', methods=['GET'])
@parser.use_args(region_argmap, location='query')
def region(args: dict) -> Response:
    result = eqtl_in_region(args['chrom'], args['start'], args['stop'])
    return make_response(jsonify(result))


@bp.route('/eqtl/region_count', methods=['GET'])
@parser.use_args(region_argmap, location='query')
def region_count(args: dict) -> Response:
    result = count_in_region(args['chrom'], args['start'], args['stop'])
    return make_response(jsonify(result))


@bp.route('/eqtl/region_tissue_count', methods=['GET'])
@parser.use_args(region_argmap, location='query')
def region_tissue_count(args: dict) -> Response:
    result = count_credible_sets_tissue_region(args['chrom'], args['start'], args['stop'])
    return make_response(jsonify(result))


@bp.route('/eqtl/ensembl_tissue_count', methods=['GET'])
@parser.use_args(ensg_argmap, location='query')
def ensembl_tissue_count(args: dict) -> Response:
    result = count_credible_sets_tissue_ensembl(args['ensembl'])
    return make_response(jsonify(result))


###################
# Implementations #
###################

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


def susie_by_id(cpra: str) -> dict:
    """ Lookup single Susie eqtl by positional id.
    @param cpra.  Positional id in the form of chrom_pos_ref_alt
    """
    pipeline = [{'$match': {'variant_id': cpra}}, {'$project': {'_id': False}}]
    cursor = current_app.mmongo.db.eqtl_susie.aggregate(pipeline)
    answer = [item for item in cursor]

    if answer is None:
        return []
    else:
        return answer


def susie_ensembl(ensembl_id: str) -> list:
    pipeline = [{'$match': {'phenotype_id': ensembl_id}}, {'$project': {'_id': False}}]
    cursor = current_app.mmongo.db.eqtl_susie.aggregate(pipeline)
    answer = [item for item in cursor]
    return answer


def susie_count(ensembl_id: str) -> int:
    mongo_filter = {'phenotype_id': ensembl_id}
    result = current_app.mmongo.db.eqtl_susie.count_documents(mongo_filter)
    return result


def eqtl_in_region(chrom: str, start: int, stop: int) -> list:
    pos_pipeline = [{'$match': {'chrom': chrom, 'pos': {'$gte': start, '$lte': stop}}},
                    {'$project': {'_id': False}}]
    cursor = current_app.mmongo.db.eqtl_susie.aggregate(pos_pipeline)
    answer = [item for item in cursor]
    return answer


def count_in_region(chrom: str, start: int, stop: int) -> int:
    mongo_filter = {'chrom': chrom, 'pos': {'$gte': start, '$lte': stop}}
    result = current_app.mmongo.db.eqtl_susie.count_documents(mongo_filter)
    return result


def count_credible_sets(match_spec: dict) -> dict:
    """
    Return count of credible sets for given match specification for a mongodb aggregation.
    """
    group_spec = {'_id': {'tissue': '$tissue', 'pheno': '$phenotype_id', 'cs': '$cs_id'},
                  'n_eqtl': {'$count': {}}}
    # Grouping to count credible sets per tissue
    count_spec = {'_id': '$_id.tissue',
                  'n_credible_set': {'$count': {}},
                  'n_eqtl': {'$sum': '$n_eqtl'}}

    pipeline = [{'$match': match_spec}, {'$group': group_spec}, {'$group': count_spec}]
    cursor = current_app.mmongo.db.eqtl_susie.aggregate(pipeline)

    answer = {}
    for item in cursor:
        answer[item['_id']] = item['n_credible_set']

    return answer


def count_credible_sets_tissue_region(chrom: str, start: int, stop: int) -> dict:
    """
    Provide count of credible sets for each tissue in specified region.
    """
    match_region = {'chrom': chrom, 'pos': {'$gte': start, '$lte': stop}}
    return count_credible_sets(match_region)


def count_credible_sets_tissue_ensembl(ensemble_id: str) -> list:
    """
    Provide count of credible sets for each tissue in transcript.
    """
    match_ensembl = {'phenotype_id': ensemble_id}
    return count_credible_sets(match_ensembl)


##########################################
# Conditional eQTL data will not be used #
#  Will be removed                       #
##########################################

@bp.route('/eqtl/cond', methods=['GET'])
@parser.use_args(eqtl_argmap, location='query')
def get_cond(args: dict) -> Response:
    if args['gene'].startswith("ENSG"):
        result = cond_ensembl(args['gene'])
    else:
        result = cond(args['gene'])
    return make_response(jsonify(result))


@bp.route('/eqtl/cond_count', methods=['GET'])
@parser.use_args(ensg_argmap, location='query')
def get_cond_count(args: dict) -> Response:
    result = cond_count(args['ensembl'])
    return make_response(jsonify(result))


@bp.route('/eqtl/cond_by_id', methods=['GET'])
@parser.use_args(eqtl_cpra_argmap, location='query')
def get_cond_by_id(args: dict) -> Response:
    result = cond_by_id(args['cpra'])
    return make_response(jsonify(result))


def cond_ensembl(ensembl_id: str) -> list:
    pipeline = [{'$match': {'phenotype_id': ensembl_id}}, {'$project': {'_id': False}}]
    cursor = current_app.mmongo.db.eqtl_cond.aggregate(pipeline)
    answer = [item for item in cursor]
    return answer


def cond_count(ensembl_id: str) -> int:
    mongo_filter = {'phenotype_id': ensembl_id}
    result = current_app.mmongo.db.eqtl_cond.count_documents(mongo_filter)
    return result


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


def cond_by_id(cpra: str) -> dict:
    """ Lookup single Susie eqtl by positional id.
    @param cpra.  Positional id in the form of chrom_pos_ref_alt
    """
    pipeline = [{'$match': {'variant_id': cpra}}, {'$project': {'_id': False}}]
    cursor = current_app.mmongo.db.eqtl_cond.aggregate(pipeline)
    answer = [item for item in cursor]

    if answer is None:
        return []
    else:
        return answer
