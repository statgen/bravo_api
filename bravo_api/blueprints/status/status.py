import logging
from flask import Blueprint, current_app, jsonify, make_response

bp = Blueprint('status', __name__)
logger = logging.getLogger(__name__)


@bp.route('/health', methods=['GET'])
def health_check():
    return make_response(jsonify({'alive': True}))


@bp.route('/version', methods=['GET'])
def version():
    if(hasattr(current_app, 'version')):
        return make_response(jsonify({'version': current_app.version}))
    else:
        return make_response(jsonify({'version': 'unknown'}))


@bp.route('/usage', methods=['GET'])
def usage():
    result = current_app.cache.get('usage')
    if result is None:
        result = active_user_count()
        current_app.cache.set('usage', result, timeout=3600)
        logger.debug("usage result updated")
    return make_response(jsonify(result))


def active_user_count():
    """
    Using mongo client of current app, query auth log for count of unique users per month.
    Return array of dicts one per month. E.g.

    [{'month': 10, 'n_users': 20, 'year': 2023},
    {'month': 9, 'n_users': 30, 'year': 2023},
    {'month': 8, 'n_users': 40, 'year': 2023}]
    """
    pipeline = [
            {"$project": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "user_id": "$user_id"}},
            {"$group": {"_id": {"month": "$month", "year": "$year"},
                        "users": {"$addToSet": "$user_id"}}},
            {"$project": {
                        "_id": 0,
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "n_users": {"$size": "$users"}}},
            {"$sort": {
                        "year": -1,
                        "month": -1}}
    ]
    # debugging
    # print("Debugging")
    # print(current_app.mmongo)
    # print(current_app.mmongo.list_collection_names())
    # print([item for item in current_app.mmongo.auth_log.find()])
    # print([item for item in current_app.mmongo.db.auth_log.find()])

    cursor = current_app.mmongo.db.auth_log.aggregate(pipeline)
    return([item for item in cursor])
