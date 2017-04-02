# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import os
import jinja2
import hashlib
import re
import random
import hmac
from string import letters

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


secret = '$he$lloworld$welcometo$myblog$'


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def make_salt(length=5):
    return ''.join(random.choice(letters) for x in range(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha512(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)
9

def users_key(group='default'):
    return ndb.Key.from_path('users', group)


class User(ndb.Model):
    firstname = ndb.StringProperty(required=True)
    lastname = ndb.StringProperty(required=True)
    joined = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty(required=True)
    pass_hash = ndb.TextProperty(required=True)

    @classmethod
    def by_id(cls,uid):
        return User.get_by_id(uid,parent=users_key())
        
    @classmethod
    def by_email(cls,email):
        u = User.all().filter('email =',email).get()
        return u

    @classmethod
    def register(cls,firstname,lastname,pw,email):
        pw_hash = make_pw_hash(email,pw)
        return User(parent=users_key(),
                    firstname = firstname,
                    lastname = lastname,
                    pass_hash=pw_hash,
                    email = email)
    
    @classmethod
    def login(cls,email,pw):
        u = cls.by_email(email)
        if u and valid_pw(email,pw,u.pass_hash):
            return u

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(Handler):
    def get(self):
        self.render('index.html')


class RegisterHandler(Handler):
    def get(self):
        self.render("register.html")

    def post(self):
        firstname = self.request.get()


class LoginHandler(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        self.write('Login Handler-POST')


class LogoutHandler(Handler):
    def get(self):
        self.render('logout.html')

    def post(self):
        self.write('Logout Handler - POST')


class PostsHandler(Handler):
    def get(self):
        self.render('posts.html')


class PostHandler(Handler):
    def get(self, post_id):
        self.render("post.html")


class NewPostHandler(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        self.write('Add a new POST')


class WelcomePageHandler(Handler):
    def get(self):
        self.render('welcome.html')


class EditPostHandler(Handler):
    def get(self, post_id):
        self.render('editpost.html')

    def post(self, post_id):
        self.write('Edit post Handler - POST %s' % post_id)


class DeletePostHandler(Handler):
    def get(self, post_id):
        self.render("delete.html")

    def post(self, post_id):
        self.write('delete post handler - POST %s' % post_id)


app = webapp2.WSGIApplication([
    (r'/', MainPage),
    (r'/register', RegisterHandler),
    (r'/posts/(\d+)/edit', EditPostHandler),
    (r'/posts/(\d+)', PostHandler),
    (r'/posts', PostsHandler),
    (r'/welcome', WelcomePageHandler),
    (r'/posts/(\d+)/delete', DeletePostHandler),
    (r'/posts/new', NewPostHandler),
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler)

], debug=True)
