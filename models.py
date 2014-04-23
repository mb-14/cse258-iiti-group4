from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    fullname = db.Column('fullname', db.String(50), index=True)
    password = db.Column('password' , db.String(250))
    department = db.Column('department' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)
    is_admin = db.Column(db.Boolean)

    def __init__(self , username, fullname, password , department, email, is_admin=False):
        self.username = username
        self.fullname = fullname
        self.set_password(password)
        self.email = email
        self.department = department
        self.is_admin = is_admin

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True
    
    def is_administrator(self):
        return self.is_admin

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
    def get_department(self):
        return self.department

    def __repr__(self):
        return '<User %r>' % (self.username)

class Docs(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    amount = db.Column(db.String)
    init_date = db.Column(db.DateTime) ## date initiated
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id')) ## initiated by
    last_user_id = db.Column(db.Integer, db.ForeignKey('users.id')) ## last recieved by
    last_approved = db.Column(db.Integer, db.ForeignKey('users.id'))  ##last approved by
    accepted = db.Column(db.Integer)
    log = db.Column(db.Text)
    desc = db.Column(db.Text) 
 
    def __init__(self, title, amount, desc):
        self.title = title
        self.amount = amount
        self.init_date = datetime.now()
        self.accepted = 0
        self.log = ''
        self.desc = desc
    
    def can_forward(self, current):
        if(self.accepted%2 == 0 and current == self.last_user_id): 
            return True
        else:
            return False

    def can_accept(self, current):
        if(self.last_user_id == current and not self.accepted%2==0 and self.accepted>=0):
            return True
        else:
            return False

    def log_approve(self, department , date):
        self.log += department+'|'+date+'|'
    
    def log_forward(self, date, remark):
        self.log += date+'|'+remark+'#'
    
    def get_init(self):
        return User.query.get(self.user_id).fullname

    def get_init_department(self):
        return User.query.get(self.user_id).department

    def get_last(self):
        return User.query.get(self.last_approved).fullname

    def get_last_department(self):
        return User.query.get(self.last_approved).department

    def get_last_date(self):
        s = self.log.split('#')
        if(len(s) == 1 or not s[1]):
            return s[0].split('|')[1]
        elif(len(s) == 2 and s[1]):
            return s[1].split('|')[1]
        else:
            return s[-2].split('|')[1]        
