import logging
import pymongo
from flask import current_app, Blueprint, jsonify, make_response, Response
from flask_cors import CORS
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE

logger = logging.getLogger(__name__)
bp = Blueprint('structvar', __name__)
CORS(bp)


class Parser(FlaskParser):
    # Override in order to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()

sv_region_argmap = {
    'chrom': fields.Str(required=False, validate=lambda x: len(x) > 0,
                        error_messages={'validator_failed': 'Value must be a non-empty string.'}),
    'start': fields.Int(required=False, validate=lambda x: x >= 0,
                        error_messages={
                            'validator_failed': 'Value must be greater than or equal to 0.'
                        }),
    'stop': fields.Int(required=False, validate=lambda x: x > 0,
                       error_messages={'validator_failed': 'Value must be greater than 0.'}),
}


@bp.route('/sv/region', methods=['GET'])
@parser.use_args(sv_region_argmap, location='query')
def get_sv_region(args: dict) -> Response:
    result = sv_region(current_app.mmongo.db.structvar, args['chrom'], args['start'], args['stop'])
    return make_response(jsonify(result))


def sv_region(structvars: pymongo.collection.Collection,
              chrom: str, roi_start: int, roi_stop: int) -> list:
    """ Lookup structual variant data by region. Include all structural variants where the pos OR
    end is within the given range of interest.

    @param structvars: Structural variants collection
    @param chrom: Chromosome containing regoin of interest.
    @param roi_start: Start position of region of interest.
    @param roi_stop: Stop position of region of interest.
    """

    pipeline = [
        {'$match': {
            '$and': [
                {'chrom': {'$eq': chrom}},
                {'$or': [
                    {'$and': [
                        {'pos': {'$gte': roi_start}},
                        {'pos': {'$lte': roi_stop}}
                    ]},
                    {'$and': [
                        {'end': {'$gte': roi_start}},
                        {'end': {'$lte': roi_stop}}
                    ]},
                    {'$and': [
                        {'pos': {'$lte': roi_start}},
                        {'end': {'$gte': roi_stop}}
                    ]}
                ]}
            ]}
         }
    ]

    cursor = structvars.aggregate(pipeline)
    return [item for item in cursor]
