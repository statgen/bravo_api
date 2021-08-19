from flask import Blueprint, jsonify, make_response

bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    return make_response(jsonify({'alive': True}))
