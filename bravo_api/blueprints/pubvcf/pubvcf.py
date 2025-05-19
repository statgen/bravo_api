import logging
from flask import Blueprint, Response, current_app, jsonify, make_response

bp = Blueprint('pubvcf', __name__)
logger = logging.getLogger(__name__)

@bp.route('/pubvcf', methods=['GET'])
def health_check():
    return make_response(jsonify({'alive': True}))
