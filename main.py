import webapp2
import jinja2
import os
from google.appengine.ext import ndb
url = 'http://localhost:8080/'

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    username_lower = ndb.ComputedProperty(lambda self: self.username.lower())
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

the_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# the handler section

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        user = self.request.cookies.get('id')
        if user:
            profile_template = the_jinja_env.get_template('templates/profile.html')
            self.response.write(profile_template.render({'username':'noob'}))
        else:
            self.redirect(url + 'form')

class FormPage(webapp2.RequestHandler):
    def get(self): #for a get request
        form_template = the_jinja_env.get_template('templates/form.html')
        self.response.write(form_template.render())  # the response
    

class SignUp(webapp2.RequestHandler):
    def get(self):
        signup_template = the_jinja_env.get_template('templates/signup.html')
        message = self.request.get('message')
        if message:
            self.response.write(signup_template.render({'message':message}))
        else:
            self.response.write(signup_template.render())

    
    def post(self):
        username = self.request.get('username')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        email = self.request.get('email').lower()
        password = self.request.get('password')

        if username and first_name and last_name and email and password:
            users = User.query()
            check_username = users.filter(User.username_lower == username.lower()).fetch() 
            check_email = users.filter(User.email == email).fetch()

            if check_username:
                self.redirect(url + 'signup?message={}'.format('username not available.'))
                return

            if check_email:
                self.redirect(url + 'signup?message={}'.format('email is already registered.'))
                return
            
            user = User(username = username,first_name = first_name, last_name = last_name, email = email, password =password)
            key = user.put()
            self.response.set_cookie('id', str(key.id()))
            self.redirect(url)
        else:
            self.redirect(url + 'signup?message={}'.format('enter all fields'))

class Login(webapp2.RequestHandler):
    def get(self):
        login_template = the_jinja_env.get_template('templates/login.html')
        message = self.request.get('message')
        if message:
            self.response.write(login_template.render({'message':message}))
        else:
            self.response.write(login_template.render())

    def post(self):
        username = self.request.get('username').lower()
        password = self.request.get('password')
        
        users = User.query()
        user_data = users.filter(User.username_lower == username).fetch() or users.filter(User.email == username).fetch()
        if user_data:
            user = user_data[0]
            if user.password == password:
                self.response.set_cookie('id', str(user.key.id()))
                self.redirect(url)
            else:
                self.redirect(url + 'login?message={}'.format('incorrect password.'))
        else:
            self.redirect(url + 'login?message={}'.format('username or email is not registered.'))
        

app = webapp2.WSGIApplication([
    ('/', ProfilePage), 
    ('/signup', SignUp),
    ('/login', Login),
    ('/form', FormPage)
], debug=True)
