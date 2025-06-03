import logging
from webargs import fields
from webargs.flaskparser import FlaskParser
from marshmallow import RAISE, validate
from flask import Blueprint, current_app, jsonify, make_response, request

bp = Blueprint('pubvcf_routes', __name__)
logger = logging.getLogger(__name__)


class Parser(FlaskParser):
    # Override in order to raise validation error for unknown args
    DEFAULT_UNKNOWN_BY_LOCATION = {"query": RAISE}


parser = Parser()

vcf_argmap = {
    'chrom': fields.Str(required=True, validate=validate.Length(min=1, max=5),
                        error_messages={'invalid_chrom': 'String length must be 1-5 characters.'}),
}


@bp.route('/link', methods=['GET'])
@parser.use_args(vcf_argmap, location='query')
def get_url():
    # current_app.pubvcf_source.get_url(args['chrom'], request.remote_user)
    logger.log(f"get vcf url for: {request.remote_user}")
    return make_response(jsonify({'url': "example.com"}))


@bp.route('/available', methods=['GET'])
def availabile_vcfs():
    return make_response(jsonify([]))
