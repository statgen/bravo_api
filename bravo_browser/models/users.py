from bravo_browser.models.database import mongo


def load(email):
   return mongo.db.users.find_one({'user_id': email}, projection = {'_id': False})


def in_whitelist(email):
   if 'whitelist' not in mongo.db.list_collection_names():
      return True
   n_documents = mongo.db.whitelist.count_documents({})
   if n_documents == 0: # if whitelist is empty, then we assume that it is desabled
      return True
   document = mongo.db.whitelist.find_one({'user_id': email}, projection = {'_id': False})
   return (document is not None)


def save(email, picture):
   result = mongo.db.users.insert_one({'user_id': email, 'picture': picture, 'agreed_to_terms': False})
   return mongo.db.users.find_one({'_id': result.inserted_id}, projection = {'_id': False})


def update_agreed_to_terms(email, agreed):
   mongo.db.users.update_one({'user_id': email}, {'$set': {'agreed_to_terms': agreed}})


def update_picture(email, picture):
   mongo.db.users.update_one({'user_id': email}, {'$set': {'picture': picture}})
