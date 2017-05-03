import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogbody = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Blog.get_by_id(int(id))

        if post:
            self.response.write("<a href='/blog'>Blog Homepage</a><br><br>")
            self.response.write("<a href='/newpost'>create new post</a>")
            self.response.write("<br><p style='font-size:30px'><strong>" + post.title + "</strong></p><br><br>" + post.blogbody + "<br><br>")
            self.response.write("<br><br>created ")
            self.response.write(post.created)
        else:
            error = "No post by that id number."
            self.response.write(error)

class MainPage(Handler):
    def render_front(self, title="", blogbody = "", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog " "ORDER BY created DESC " "LIMIT 5 ")
        self.render("front.html", title=title, blogbody=blogbody, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class NewPostPage(Handler):
    def render_newpost(self, title="", blogbody = "", error=""):
        self.render("newpost.html", title=title, blogbody=blogbody, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        blogbody = self.request.get("blogbody")

        if title and blogbody:
            a = Blog(title = title, blogbody = blogbody)
            a.put()

            self.redirect("/blog")

        else:
            error = "we need both a title and some words!"
            self.render_newpost(title, blogbody, error)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPostPage),
    ('/blog', MainPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
