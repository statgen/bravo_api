from flask_pymongo import PyMongo
import click
from flask.cli import with_appcontext
import sys


mongo = PyMongo()


@click.command('create-users')
@with_appcontext
def create_users():
    """DESCRIPTION:

    Creates empty 'users' collections."""
    mongo.db.users.drop()
    mongo.db.users.create_index('user_id')
    sys.stdout.write("Created empty 'users' collection.\n")


@click.command('load-whitelist')
@click.argument('whitelist_file', type=click.Path(exists=True))
def load_whitelist(whitelist_file):
    """DESCRIPTION:

    Creates and populates the 'whitelist' collection.

    ARGUMENTS:

    whitelist_file -- file with emails (one email per line)
    """
    mongo.db.whitelist.drop()
    with open(whitelist_file, 'r') as ifile:
        for line in ifile:
            email = line.strip()
            if email and '@' in email:
                mongo.db.whitelist.insert({'user_id': email})
    mongo.db.whitelist.create_index('user_id')
    sys.stdout.write(f"Created 'whitelist' collection and inserted "
                     f"{mongo.db.whitelist.count()} email(s).\n ")
