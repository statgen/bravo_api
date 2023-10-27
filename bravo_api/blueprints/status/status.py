import logging
import pymongo
import sys
from flask import Blueprint, Response, current_app, jsonify, make_response

bp = Blueprint('status', __name__)
logger = logging.getLogger(__name__)


@bp.cli.command('print_routes')
def print_routes():
    """
    Command line convenience for printing all the routes for the application.
    Useful when external testers need list of routes.
    """
    current_app.url_map
    routes = [str(item) for item in current_app.url_map.iter_rules()]
    sys.stdout.write("Routes Map:\n")
    for route in routes:
        sys.stdout.write(f"{route}\n")


@bp.route('/health', methods=['GET'])
def health_check():
    return make_response(jsonify({'alive': True}))


@bp.route('/version', methods=['GET'])
def version() -> Response:
    if(hasattr(current_app, 'version')):
        return make_response(jsonify({'version': current_app.version}))
    else:
        return make_response(jsonify({'version': 'unknown'}))


@bp.route('/usage', methods=['GET'])
def usage() -> Response:
    result = current_app.cache.get('usage')
    if result is None:
        result = usage_stats(current_app.mmongo.db)
        current_app.cache.set('usage', result, timeout=3600)
        logger.debug("Usage result updated")
    return make_response(jsonify(result))


def usage_stats(db: pymongo.database.Database) -> dict:
    """
    Given a mongo database, run queries to compile statistics about user usage of API.
    """
    result = {"active": active_user_count(db.auth_log),
              "new": new_user_count(db.users),
              "total": total_user_count(db.users)}
    return result


def total_user_count(collection: pymongo.collection.Collection) -> int:
    """
    Using users collection, query count of users that have agreed to terms.
    Return count of users that have agreed to terms of service.
    """
    cursor = collection.find({"agreed_to_terms": {"$eq": True}})
    return len([item for item in cursor])


def new_user_count(collection: pymongo.collection.Collection) -> dict:
    """
    Given users collection, query for new users that agreed to terms per month.
    Return array of dicts one per month. E.g.

    [{'month': 10, 'new_users': 20, 'year': 2023},
    {'month': 9, 'new_users': 30, 'year': 2023},
    {'month': 8, 'new_users': 40, 'year': 2023}]
    """
    user_counts_pline = [
        {"$match": {"agreed_to_terms": {"$eq": True}}},
        {"$project": {
            "year": {"$year": "$agreed_date"},
            "month": {"$month": "$agreed_date"}}},
        {"$group": {
            "_id": {"month": "$month",
                    "year": "$year"},
            "new_users": {"$sum": 1}}},
        {"$project": {
                    "_id": 0,
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "new_users": 1}},
        {"$sort": {"year": -1, "month": -1}}
    ]

    user_counts = collection.aggregate(user_counts_pline)
    return [item for item in user_counts]


def active_user_count(collection: pymongo.collection.Collection) -> dict:
    """
    Given pymongo collection for the auth log, query for count of unique users per month.
    Return array of dicts one per month. E.g.

    [{'month': 10, 'active_users': 20, 'year': 2023},
    {'month': 9, 'active_users': 30, 'year': 2023},
    {'month': 8, 'active_users': 40, 'year': 2023}]
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
                        "active_users": {"$size": "$users"}}},
            {"$sort": {"year": -1, "month": -1}}
    ]

    cursor = collection.aggregate(pipeline)
    return([item for item in cursor])
