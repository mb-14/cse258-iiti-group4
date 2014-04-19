from flask import  request, flash, url_for, redirect, render_template
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from app import app
from models import *
from flask.ext.login import current_user 

class AdminView(BaseView):
    
    @expose('/')
    def index(self):
        return redirect(url_for('adminview.register')) 
    
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.is_administrator():
            return True
        return False

    @expose('/register/' , methods=['GET','POST'])
    def register(self):
       if request.method == 'GET':
           return self.render('register.html')
       user = User(request.form['username'] ,request.form['fullname'], request.form['password'],request.form['department'],request.form['email'],False)
       db.session.add(user)
       db.session.commit()
       flash('User successfully registered')
       return redirect(url_for('adminview.register'))


class UserView(ModelView):
    column_exclude_list = ['password']
    column_list=('username','email','department','is_admin')
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.is_administrator():
            return True
        return False

class DocView(ModelView):
    can_edit = False
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.is_administrator():
            return True
        return False

admin = Admin(app)
admin.add_view(AdminView(name='Register'))
admin.add_view(UserView(User, db.session))
admin.add_view(DocView(Docs, db.session))
