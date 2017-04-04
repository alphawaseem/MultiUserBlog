from google.appengine.ext import db
from passwordlib import make_pw_hash,verify_pw_hash

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
    comments = db.StringListProperty()
    likes = db.IntegerProperty()

    @classmethod
    def add_post(cls,title,content,user_id):
        return Post(title=title,content=content,user_id = user_id)
    
    @classmethod
    def like_post(cls,post_id):
        post = Post.get_by_id(post_id)
        if post.likes:
            post.likes += 1
        else:
            post.likes = 1
        return post
    @classmethod
    def user_posts(cls,uid):
        return Post.all().filter('user_id =',uid).order('-added')