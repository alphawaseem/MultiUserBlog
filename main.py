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

from google.appengine.ext import db

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
    return db.Key.from_path('users', group)


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
    def login(cls, email, pw):
        u = cls.by_email(email)
        if u and valid_pw(email, pw, u.pass_hash):
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
        val = self.read_secure_cookie('user_id')
        if val:
            self.redirect('/welcome')
        self.render("register.html")

    def email_exists(self, email):
        if User.by_email(email):
            return True
        return False

    def password_matched(self, p1, p2):
        return p1 == p2

    def post(self):
        self.firstname = self.request.get('firstname')
        self.lastname = self.request.get('lastname')
        self.email = self.request.get('email')
        self.password = self.request.get('password')
        self.password1 = self.request.get('password1')
        self.agree = self.request.get('agree')

        params = dict(firstname=self.firstname,
                      lastname=self.lastname, email=self.email)
        have_error = False
        if self.email_exists(self.email):
            params['error_email'] = 'You cannot use this email. It might have already taken!'
            have_error = True

        if not self.password_matched(self.password, self.password1):
            params['error_pass_mismatch'] = 'Passwords do not match'
            have_error = True

        if not self.agree:
            params['error_agree_terms'] = 'You must agree to terms and conditions of the website.'
            have_error = True
        if have_error:
            self.render('register.html', **params)
        else:
            u = User.register(self.firstname, self.lastname,
                              self.password, self.email)
            u.put()
            self.login(u)
            self.redirect("/welcome")


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
        uid = self.read_secure_cookie('user_id')
        if uid:
            user = User.by_id(int(uid))
            self.render('welcome.html', user = user)
        else:
            self.redirect('/login')

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
