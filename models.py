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
    init_date = db.Column(db.DateTime) ## date initiated
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id')) ## initiated by
    last_user_id = db.Column(db.Integer, db.ForeignKey('users.id')) ## last recieved by
    accepted = db.Column(db.Boolean) 
 
    def __init__(self, title, amount):
        self.title = title
        self.amount = amount
        self.init_date = datetime.utcnow()
        self.accepted = False
    
    def can_forward(self, current):
        if(self.user_id == current and self.last_user_id == self.user_id): #if current user is the initiator
            return True
        if(self.last_user_id == current and self.accepted): #if current user is the last user to recieve and has accept
            return True
        else:
            return False

    def can_accept(self, current):
        if(self.last_user_id == current and not self.accepted):
            return True
        else:
            return False


            
