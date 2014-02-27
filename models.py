from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(250))
    department = db.Column('department' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)

    def __init__(self , username ,password , department, email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.department = department

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class Docs(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    amount = db.Column(db.String)
    init_date = db.Column(db.DateTime)
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id'))
 
    def __init__(self, title, amount):
        self.title = title
        self.amount = amount
        self.init_date = datetime.utcnow()
