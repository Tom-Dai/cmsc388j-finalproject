from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time



@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()



class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_picture = db.ImageField()
    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=1, max_length=500)
    date = db.StringField(required=True)
    anime_id = db.StringField(required=True)
    anime_title = db.StringField(required=True, min_length=1, max_length=100)
    rating = db.IntField(required=True)

#remember to create a watchlist collection
class Watchlist(db.Document):
    user = db.ReferenceField(User, required=True)
    name = db.StringField(required = True)
    anime_ids = db.ListField(db.StringField())