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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

class MainPage(Handler):
    def render_front(self,error="",subject="",content=""):
        posts = ndb.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        visits = self.request.cookies.get('visits','0')
        if visits and visits.isdigit():
            visits = int(visits)+1
        else:
            visits = 0
        self.response.headers.add_header('Set-Cookie','visits=%s'%visits)
        self.render("form.html",error = error , subject = subject , content = content,posts = posts,visits = visits)
    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            self.addPost(subject,content)
        else:
            error = "Please enter subject and content"
            self.render_front(error,subject,content)
        
    def addPost(self,subject,content):
        a = Post(subject=subject,content=content)
        a.put()
        self.render_front()

def blog_key(name='default'):
    return ndb.Key.from_path('blogs',name)

class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)


    def render(self):
        self._render_text = self.content.replace('\n','<br>')
        return render_str("post.html",p=self)
class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    passw = ndb.StringProperty(required=True)
    joined = ndb.DateTimeProperty(auto_now_add = True)
    

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
