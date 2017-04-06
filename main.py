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
import re


from cookielib import encrypt_cookie_value, decrypt_cookie_value
from passwordlib import make_pw_hash, verify_pw_hash
from models import User, Post, Comment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


################################# BASE HANDLERS #############################
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_form_value(self, field_name):
        return self.request.get(field_name)


class CookieHandler(Handler):
    def set_secure_cookie(self, name, val):
        cookie_val = encrypt_cookie_value(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and decrypt_cookie_value(cookie_val)


class UserCookieHandler(CookieHandler):
    def login_user(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout_user(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def get_loggedin_user(self):
        return self.read_secure_cookie('user_id')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.get_loggedin_user()
        self.user = uid and User.by_id(int(uid))


class SecurePagesHandler(UserCookieHandler):
    def initialize(self, *a, **kw):
        super(SecurePagesHandler, self).initialize(*a, **kw)
        if not self.user:
            self.redirect('/login')


class SecurePostHandler(SecurePagesHandler):
    def set_post(self, post_id):
        self.blog_post = Post.get_by_id(int(post_id))
        if self.blog_post:
            return self.blog_post
        else:
            self.redirect('/welcome')

    def post_belongs_to_user(self):
        if self.user and self.blog_post:
            return str(self.user.key().id()) == self.blog_post.user_id
        return False


################################# PUBLIC PAGE HANDLERS ###################
class MainPage(UserCookieHandler):
    def get(self):
        posts = Post.all().order('-added').fetch(10)
        self.render('index.html', user=self.user, posts=posts)


class RegisterHandler(UserCookieHandler):
    def get(self):
        if self.user:
            self.redirect('/welcome')
        self.render("register.html")

    def email_exists(self, email):
        if User.by_email(email):
            return True
        return False

    def password_matched(self, p1, p2):
        return p1 == p2

    def post(self):
        if not self.user:
            firstname = self.get_form_value('firstname')
            lastname = self.get_form_value('lastname')
            email = self.get_form_value('email')
            password = self.get_form_value('password')
            password1 = self.get_form_value('password1')
            agree = self.get_form_value('agree')

            params = dict(firstname=firstname,
                          lastname=lastname, email=email)
            have_error = False
            if self.email_exists(email):
                params['error_email'] = 'You cannot use this email. It might have already taken!'
                have_error = True

            if not self.password_matched(password, password1):
                params['error_pass_mismatch'] = 'Passwords do not match'
                have_error = True

            if not agree:
                params['error_agree_terms'] = 'You must agree to terms and conditions of the website.'
                have_error = True
            if have_error:
                self.render('register.html', **params)
            else:
                u = User.register(firstname, lastname,
                                  password, email)
                u.put()
                self.login_user(u)
                self.redirect("/welcome")


class LoginHandler(UserCookieHandler):
    def get(self):
        if not self.user:
            self.render('login.html')
        else:
            self.redirect('/welcome')

    def post(self):
        email = self.get_form_value('email')
        password = self.get_form_value('password')
        if email and password:
            user = User.verify_user(email, password)
            if user:
                self.login_user(user)
                self.redirect('/welcome')
                return
        params = dict(email=email, password=password)
        params['errors'] = 'Invalid email or password'
        self.render('login.html', **params)


class PostsHandler(UserCookieHandler):
    def get(self):
        posts = Post.all().order('-added')
        self.render('posts.html', posts=posts, user=self.user)


class PostHandler(UserCookieHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            if self.user:
                self.redirect('/welcome')
            else:
                self.redirect('/')
        else:
            comments = Comment.all().filter('post_id =', post_id).order('-added')
            if self.user:
                self.render("post.html", user=self.user, post=post,
                            belongs_to_user=str(self.user.key().id()) == post.user_id, comments=comments)
            else:
                self.render("post.html", post=post,
                            belongs_to_user=False, comments=comments)


############################# SECURE USER PAGE HANDLERS ##################
class LogoutHandler(SecurePagesHandler):
    def get(self):
        self.render('logout.html', user=self.user)

    def post(self):
        self.logout_user()
        self.redirect('/')


class NewPostHandler(SecurePagesHandler):
    def get(self):
        self.render('newpost.html', user=self.user)

    def post(self):
        title = self.get_form_value('title')
        content = self.get_form_value('content')
        if title and content:
            post = Post.add_post(
                title=title, content=content, user_id=str(self.user.key().id()))
            post.put()
            self.redirect('/posts/%s' % post.key().id())
        else:
            error = 'Please enter both title and content'
            self.render('newpost.html', user=self.user,
                        title=title, content=content, error=error)


class WelcomePageHandler(SecurePagesHandler):
    def get(self):
        if self.user:
            posts = Post.user_posts(str(self.user.key().id()))
            self.render('welcome.html', posts=posts, user=self.user)


###################  SECURE USER WITH BLOG POSTS PAGE HANDLERS ###########
class LikePostHandler(SecurePostHandler):
    def get(self, post_id):
        self.redirect('/posts/' + post_id)

    def post(self, post_id):
        message = ''
        self.set_post(post_id)
        if not self.post_belongs_to_user() and self.user:
            self.blog_post = self.blog_post.like_post(
                str(self.user.key().id()))
            self.blog_post.put()
            self.redirect('/posts/' + post_id)
        else:
            message = 'You cannot like your own post!'
        self.render('/post.html', user=self.user, post=self.blog_post,
                    message=message)


class EditPostHandler(SecurePostHandler):
    def get(self, post_id):
        self.set_post(post_id)
        if not self.post_belongs_to_user():
            self.redirect('/posts/' + post_id)
        if self.user and self.blog_post:
            self.render('editpost.html', user=self.user, post=self.blog_post)

    def post(self, post_id):
        title = self.get_form_value('title')
        content = self.get_form_value('content')
        if title and content:
            self.set_post(post_id)
            if self.post_belongs_to_user():
                self.blog_post.title = title
                self.blog_post.content = content
                self.blog_post.put()
            self.redirect('/posts/' + post_id)
        else:
            error = 'You must provide both title and content!'
            self.render('editpost.html', error=error, title=title,
                        content=content, user=self.user)


class DeletePostHandler(SecurePostHandler):
    def get(self, post_id):
        self.set_post(post_id)
        if self.post_belongs_to_user():
            self.render('delete.html', user=self.user, post=self.blog_post)
        else:
            self.redirect('/posts/' + post_id)

    def post(self, post_id):
        self.set_post(post_id)
        if self.post_belongs_to_user():
            Post.delete(self.blog_post)
        self.redirect('/welcome')


class CommentHandler(SecurePostHandler):
    def get(self, post_id):
        self.redirect('/posts/' + post_id)

    def post(self, post_id):
        if self.user:
            comment = self.get_form_value('comment')
            if comment:
                Comment.add(comment=comment,
                            user_id=str(self.user.key().id()),
                            post_id=post_id,
                            user_name=self.user.firstname).put()
                print('comment added')
            self.redirect('/posts/' + post_id)
        else:
            self.redirect('/login')


class DeleteCommentHandler(SecurePagesHandler):
    def get(self, post_id, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        if comment and self.user and str(self.user.key().id()) == comment.user_id:
            self.render('deletecomment.html',
                        user=self.user, comment=comment)
        else:
            self.redirect('/posts/' + post_id)

    def post(self, post_id, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        if comment and self.user and str(self.user.key().id()) == comment.user_id:
            Comment.delete(comment)
        self.redirect('/posts/' + post_id)


class EditCommentHandler(SecurePostHandler):
    def get(self, post_id, comment_id):
        self.set_post(post_id)
        comment = Comment.get_by_id(int(comment_id))
        if comment and self.user and str(self.user.key().id()) == comment.user_id:
            self.render('editcomment.html', user=self.user,
                        post=self.blog_post, comment=comment)
        else:
            self.redirect('/posts/' + post_id)

    def post(self, post_id, comment_id):
        self.set_post(post_id)
        comment = Comment.get_by_id(int(comment_id))
        if comment and self.user and str(self.user.key().id()) == comment.user_id:
            new_comment = self.get_form_value('comment')
            if new_comment:
                comment.comment = new_comment
                comment.put()
                self.redirect('/posts/' + post_id)
            else:
                message = 'Please Enter New Comment!'
                self.render('editcomment.html', user=self.user,
                            comment=comment, post=self.blog_post, message=message)
        else:
            self.redirect('/posts/' + post_id)


app = webapp2.WSGIApplication([
    (r'/', MainPage),
    (r'/register', RegisterHandler),
    (r'/posts/(\d+)/edit', EditPostHandler),
    (r'/posts/(\d+)', PostHandler),
    (r'/posts', PostsHandler),
    (r'/welcome', WelcomePageHandler),
    (r'/posts/(\d+)/delete', DeletePostHandler),
    (r'/posts/(\d+)/comment', CommentHandler),
    (r'/posts/(\d+)/like', LikePostHandler),
    (r'/posts/(\d+)/(\d+)/edit', EditCommentHandler),
    (r'/posts/(\d+)/(\d+)/delete', DeleteCommentHandler),
    (r'/posts/new', NewPostHandler),
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler)

], debug=True)
