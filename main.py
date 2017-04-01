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

from google.appengine.ext import ndb
# from google.cloud import datastore

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.write('Main Page Handler')


class RegisterHandler(Handler):
    def get(self):
        self.write('Register Page Handler')

    def post(self):
        self.write('Register user to database handler')


class LoginHandler(Handler):
    def get(self):
        self.write('Login Handler-GET')

    def post(self):
        self.write('Login Handler-POST')


class LogoutHandler(Handler):
    def get(self):
        self.write('Logout Handler - GET')

    def post(self):
        self.write('Logout Handler - POST')


class PostsHandler(Handler):
    def get(self):
        self.write('Blogs Handler')


class PostHandler(Handler):
    def get(self, post_id):
        self.write('My post %s' % post_id)


class NewPostHandler(Handler):
    def get(self):
        self.write('Add a new Post - GET')

    def post(self):
        self.write('Add a new POST')


class WelcomePageHandler(Handler):
    def get(self):
        self.write('Welcome user handler')


class EditPostHandler(Handler):
    def get(self, post_id):
        self.write('Edit post handler - GET %s' % post_id)

    def post(self, post_id):
        self.write('Edit post Handler - POST %s' % post_id)


class DeletePostHandler(Handler):
    def get(self, post_id):
        self.write('Delete post handler - GET %s' % post_id)

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
