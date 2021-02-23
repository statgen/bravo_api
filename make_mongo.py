#!/usr/bin/env python

import pymongo
import bson.json_util
import os


def main():
    print("--- begin")

    db_name = "bravo-demo"

    m_client = pymongo.MongoClient("mongodb://localhost:27017")
    m_database = m_client[db_name]
    db_list = m_client.list_database_names()

    # Drop database if already present
    if db_name in db_list:
        print(f"{db_name} database exists already")
        m_client.drop_database(db_name)
        print(f"{db_name} dropped")

    # Enumerate files in mongo fixtures directory as collections
    fixtures_dir = os.path.join('tests', 'mongo_fixtures')
    for entry in os.scandir(fixtures_dir):
        collection_name = os.path.splitext(entry.name)[0]
        print(collection_name)

        collection = m_database[collection_name]
        with open(entry.path) as infile:
            data = bson.json_util.loads(infile.read())
            collection.insert_many(data)

    print("--- done")


if __name__ == "__main__":
    main()
