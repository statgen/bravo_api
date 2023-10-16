from flask import Blueprint, current_app, jsonify, make_response

bp = Blueprint('status', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    return make_response(jsonify({'alive': True}))


@bp.route('/version', methods=['GET'])
def version():
    if(hasattr(current_app, 'version')):
        return make_response(jsonify({'version': current_app.version}))
    else:
        return make_response(jsonify({'version': 'unknown'}))
