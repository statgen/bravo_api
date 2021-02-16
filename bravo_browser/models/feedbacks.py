from bravo_browser.models.database import mongo


def save(email, page, message):
    if message.strip() and page.strip():
        mongo.db.feedbacks.insert_one({'user_id': email, 'page': page, 'message': message})
