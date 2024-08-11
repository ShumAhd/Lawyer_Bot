# user_manager.py

class User:
    def __init__(self, name):
        self.name = name
        self.phone = None
        self.question = None

class UserManager:
    def __init__(self):
        self.user_dict = {}

    def add_user(self, chat_id, user):
        self.user_dict[chat_id] = user

    def get_user(self, chat_id):
        return self.user_dict.get(chat_id, None)
