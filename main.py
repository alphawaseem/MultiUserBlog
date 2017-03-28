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

from google.appengine.ext import db

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
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("form.html",error = error , subject = subject , content = content,posts = posts)
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
    return db.Key.from_path('blogs',name)

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n','<br>')
        return render_str("post.html",p=self)

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
