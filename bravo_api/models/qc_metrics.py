from bravo_api.models.database import mongo
from flask import current_app
import pymongo


def get_metrics(name):
    if name is not None:
        mongo_filter = {'name': name}
    else:
        mongo_filter = {}

    cursor = mongo.db.qc_metrics.find(mongo_filter)
    data = []
    for entry in cursor:
        entry.pop('_id')
        data.append(entry)
    return data
