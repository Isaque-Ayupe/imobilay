class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        if not user_id:
            raise ValueError("user_id must be provided")
        return self.db.find_user(user_id)

    def create_user(self, username, email):
        user = {"username": username, "email": email}
        self.db.save(user)
        return user
