#!/usr/bin/env python

import pymongo
import bson.json_util

# Pry like behavior
# import code  # Use like pry
# import inspect  # Also needed for prying


def main():
    print("--- begin")

    db_name = "bravo-demo"

    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_db = m_client[db_name]
    db_list = m_client.list_database_names()

    if "demo" in db_list:
        print("database exists already")
        m_client.drop_database(db_name)
        print("db dropped")

    with open('demo_mongo_samples.json') as infile:
        in_string = infile.read()
        data = bson.json_util.loads(in_string)

    # code.interact(local=dict(globals(), **locals()))  # binding.pry

    # create collections & records
    for key in data.keys():
        print(key)
        coll = m_db[key]
        if data[key] is not None:
            coll.insert_one(data[key])
    print("--- done")


if __name__ == "__main__":
    main()
