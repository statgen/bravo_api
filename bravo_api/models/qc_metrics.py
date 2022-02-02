from bravo_api.models.database import mongo


def get_metrics(name=None):
    if name is None:
        mongo_filter = {}
    else:
        mongo_filter = {'name': name}

    cursor = mongo.db.qc_metrics.find(mongo_filter)
    data = []
    for entry in cursor:
        entry.pop('_id')
        data.append(entry)
    return data
