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
        current_app.cache.set('usage', result, timeout=300)
    return make_response(jsonify(result))


@bp.route('/counts', methods=['GET'])
def counts() -> Response:
    result = current_app.cache.get('counts')
    if result is None:
        snv_count = count_collection(current_app.mmongo.db.snv)
        transcript_count = count_collection(current_app.mmongo.db.transcripts)
        gene_count = count_collection(current_app.mmongo.db.genes)

        result = {'snvs': snv_count, 'transcripts': transcript_count, 'genes': gene_count}

        current_app.cache.set('counts', result, timeout=3600)
        logger.debug('variant counts updated')
    return make_response(jsonify(result))


def count_collection(collection: pymongo.collection.Collection) -> int:
    """
    Count (estimate) the number of snv in backing database
    """
    result = collection.estimated_document_count()
    return result


def usage_stats(db: pymongo.database.Database) -> dict:
    """
    Given a mongo database, run queries to compile statistics about user usage of API.
    """
    result = {"active": active_user_count(db.auth_log),
              "new": new_user_count(db.users),
              "total": total_user_count(db.users),
              "max_user_per_day": max_users_per_day(db.auth_log)}
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


def max_users_per_day(collection: pymongo.collection.Collection) -> dict:
    """
    Given pymongo collection for the auth log, query for count of max users in a day per month.
    Return array of dicts one per month. E.g.

    [{'month': 10, 'max_daily_users': 10, 'year': 2023},
    {'month': 9, 'max_daily_users': 20, 'year': 2023},
    {'month': 8, 'max_daily_users': 25, 'year': 2023}]
    """
    pipeline = [
            {"$project": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "day": {"$dayOfMonth": "$timestamp"},
                        "user_id": "$user_id"}},
            {"$group": {"_id": {"day": "$day", "month": "$month", "year": "$year"},
                        "users": {"$addToSet": "$user_id"}}},
            {"$project": {
                        "_id": 0,
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "day": "$_id.day",
                        "active_users": {"$size": "$users"}}},
            {"$group": {"_id": {"month": "$month", "year": "$year"},
                        "max_user_per_day": {"$max": "$active_users"}}},
            {"$project": {
                        "_id": 0,
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "max_user_per_day": 1}},
            {"$sort": {"year": -1, "month": -1}}
    ]

    cursor = collection.aggregate(pipeline)
    return([item for item in cursor])
