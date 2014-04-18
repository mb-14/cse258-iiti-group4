from flask import  request, flash, url_for, redirect, render_template
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from app import app
from models import *

class AdminView(BaseView):
    @expose('/' , methods=['GET','POST'])
    def register(self):
       if request.method == 'GET':
           return self.render('register.html')
       user = User(request.form['username'] ,request.form['fullname'], request.form['password'],request.form['department'],request.form['email'])
       db.session.add(user)
       db.session.commit()
       flash('User successfully registered')
       return redirect(url_for('adminview.register'))

admin = Admin(app)
admin.add_view(AdminView(name='Register'))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Docs, db.session))


