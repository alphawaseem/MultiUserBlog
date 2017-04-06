from google.appengine.ext import db
from passwordlib import make_pw_hash, verify_pw_hash


class User(db.Model):
    firstname = db.StringProperty(required=True)
    lastname = db.StringProperty(required=True)
    joined = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty(required=True)
    pass_hash = db.TextProperty(required=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_email(cls, email):
        user = User.all().filter('email =', email).get()
        return user

    @classmethod
    def register(cls, firstname, lastname, pw, email):
        pw_hash = make_pw_hash(email, pw)
        return User(firstname=firstname, lastname=lastname,
                    pass_hash=pw_hash,
                    email=email)

    @classmethod
    def verify_user(cls, email, pw):
        u = cls.by_email(email)
        if u and verify_pw_hash(email, pw, u.pass_hash):
            return u


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    user_id = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    likes = db.StringListProperty()

    @classmethod
    def add_post(cls, title, content, user_id):
        return Post(title=title, content=content, user_id=user_id)

    def like_post(self, user_id):
        post = self
        if user_id not in post.likes:
            post.likes.append(user_id)
        return post

    @classmethod
    def user_posts(cls, uid):
        return Post.all().filter('user_id =', uid).order('-added')


class Comment(db.Model):
    comment = db.StringProperty(required=True)
    user_id = db.StringProperty(required=True)
    post_id = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def add(cls, comment, user_id, post_id, user_name):
        return Comment(comment=comment, user_id=user_id, post_id=post_id, user_name=user_name)
