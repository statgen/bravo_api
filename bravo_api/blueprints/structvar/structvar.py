import logging
import pymongo
import re
from flask import current_app, Blueprint, jsonify, make_response, Response
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE

logger = logging.getLogger(__name__)
bp = Blueprint('structvar', __name__)

##########
# Routes #
##########


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

sv_alignments_argmap = {
    'svid': fields.Str(required=False, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}

sv_cram_argmap = {
    'svid': fields.Str(required=False, validate=lambda x: len(x) > 0,
                       error_messages={'validator_failed': 'Value must be a non-empty string.'})
}


@bp.route('/sv/region', methods=['GET'])
@parser.use_args(sv_region_argmap, location='query')
def get_sv_region(args: dict) -> Response:
    result = sv_region(current_app.mmongo.db.sv_list, args['chrom'], args['start'], args['stop'])
    return make_response(jsonify(result))


@bp.route('/sv/debug', methods=['GET'])
def sv_debug():
    bam_data = current_app.sv_cram_source.putative_extract_cram()

    response = make_response(bam_data, 206)
    # response.headers['Content-Range'] = \
    #     f'bytes {result["start_byte"]}-{result["stop_byte"]}/{result["file_size"]}'
    response.mimetype = 'application/octet-stream'
    response.direct_passthrough = True

    return response


@bp.route('/sv/cram', methods=['GET'])
@parser.use_args(sv_cram_argmap, location='query')
def sv_cram(args: dict) -> Response:

    bam_data = current_app.sv_cram_source.get_cram_data(args['svid'])

    response = make_response(bam_data, 206)
    response.mimetype = 'application/octet-stream'
    response.direct_passthrough = True

    return response

###################
# Data Processing #
###################


ID_PATT = re.compile(r"^(INV|DUP|DEL)_(\d\d?):\d+-\d+$", re.IGNORECASE)
SV_TYPES = ["INV", "DEL", "DUP"]
CHROMS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
          "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "X"]
MAX_POS = 250_000_000


def is_sv_id_well_formed(sv_id: str) -> bool:
    if re.fullmatch(ID_PATT, sv_id):
        return True
    return False


def is_sv_id_valid(sv_id: str) -> bool:
    """
    Sequentially examine a well formed structural variant id to ensure it is logically valid.
    Variant type must be from the defined set.
    chromosome must be from the defined set.
    Stop position must be greater than the start position.
    Stop position must be smaller than maximum basepair position
    """
    # variant type
    sv_type, rem = sv_id.split("_")
    if not any(sv_type == item for item in SV_TYPES):
        return False

    # chromosome range
    chrom, rem = rem.split(":")
    if not any(chrom == item for item in CHROMS):
        return False

    # start and stop must be in order
    start, stop = rem.split("-")
    istart = int(start)
    istop = int(stop)
    if istart > istop:
        return False

    if istop > MAX_POS:
        return False

    return True


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
         },
        {'$project': {'_id': 0}}
    ]

    cursor = structvars.aggregate(pipeline)
    return [item for item in cursor]


def sv_alignments(aligns: pymongo.collection.Collection, sv_id: str) -> dict:
    logger.debug(f"Getting Alignments for {sv_id}")
    return(aligns.find_one({"sv_id": sv_id}))
