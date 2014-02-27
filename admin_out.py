from flask.ext.admin import Admin, BaseView, expose
from app import app
from models import *


admin = Admin(app)
admin.add_view(AdminView(name='Register'))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Docs, db.session))

class AdminView(BaseView):
    @expose('/' , methods=['GET','POST'])
    def register():
       if request.method == 'GET':
           return render_template('register.html')
       user = User(request.form['username'] , request.form['password'],request.form['department'],request.form['email'])
       db.session.add(user)
       db.session.commit()
       flash('User successfully registered')
       return redirect(url_for('register'))
