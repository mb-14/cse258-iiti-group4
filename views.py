from flask import session, request, flash, url_for, redirect, render_template, abort ,g
from app import app
from datetime import datetime
from models import *
from flask.ext.login import login_user , logout_user , current_user , login_required
from functools import wraps

def canforward(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        doc_id = kwargs['doc_id']
        if (not Docs.query.get(doc_id).can_forward(g.user.id)):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def canclose(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        doc_id = kwargs['doc_id']
        if (not (Docs.query.get(doc_id).can_forward(g.user.id) and g.user.department == 'Accounts')):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/all', methods=['GET', 'POST'])
@login_required
def alldocs():
    if g.user.is_authenticated():
        if request.method == 'POST':
            doc_id = request.form['accept']
            doc_item = Docs.query.get(doc_id)
            doc_item.accepted += 1
            doc_item.last_approved = g.user.id
            doc_item.log_approve(g.user.department,datetime.now().strftime('%b %d, %G %I:%M %p'))
            db.session.commit()
            flash('Document accepted')
            redirect(url_for('alldocs'))
        return render_template('alldocs.html',docs=Docs.query.all(),current=g.user.id)
    else:
        return redirect(url_for('login'))	

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if g.user.is_authenticated():
        if request.method == 'POST':
            doc_id = request.form['accept']
            doc_item = Docs.query.get(doc_id)
            doc_item.accepted += 1
            doc_item.last_approved = g.user.id
            doc_item.log_approve(g.user.department,datetime.now().strftime('%b %d, %G %I:%M %p'))
            db.session.commit()
            flash('Document accepted')
            redirect(url_for('index'))
        return render_template('mydocs.html',docs=Docs.query.filter((Docs.user_id == g.user.id) | (Docs.last_user_id== g.user.id)).all(),current=g.user.id)
    else:
        return redirect(url_for('login'))		

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        if not request.form['title']:
            flash('Title is required', 'error')
        elif not request.form['amount']:
            flash('Amount is required', 'error')
        else:
            doc = Docs(request.form['title'], request.form['amount'], request.form['desc'])
            doc.last_user_id = doc.user_id = g.user.id
            doc.last_approved = doc.last_user_id
            doc.log_approve(g.user.department,'NA')
            db.session.add(doc)
            db.session.commit()
            flash('Document was successfully created')
            return redirect(url_for('index'))
    return render_template('new.html')


@app.route('/changepass', methods=['GET', 'POST'])
@login_required
def changepass():
    if request.method == 'POST':
        if(request.form['newpass'] != request.form['newpass1']):
            flash('Password mismatch','error')
        else:
            user = User.query.get(g.user.id)
            user.set_password(request.form['newpass'])
            db.session.commit()
            flash('Password successfully changed')
            return redirect(url_for('index'))
    return render_template('changepass.html')


@app.route('/doc/<int:doc_id>')
@login_required
def show(doc_id):
    doc_item = Docs.query.get(doc_id)
    return render_template('view.html',doc=doc_item,name=User.query.get(doc_item.user_id).fullname)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['username']
    email = request.form['username']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
    if registered_user is None:
        flash('Username is invalid' , 'error')
        return redirect(url_for('login'))
    if not registered_user.check_password(password):
        flash('Password is invalid','error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/forward/<int:doc_id>',methods=['GET','POST'])
@login_required
@canforward
def forward(doc_id):
    doc_item = Docs.query.get(doc_id)
    if request.method == 'GET':
        return render_template('forward.html',doc=doc_item,users = [user.email for user in User.query.all()])
    
    recipient = request.form['recipient']
    fullname = request.form['recipient']
    remark = request.form['remark']
    registered_user = User.query.filter_by(email=recipient).first() or User.query.filter_by(fullname=recipient).first()
    if registered_user is None:
        flash('Recipient email ID does not exist' , 'error')
        return redirect(url_for('forward',doc_id=doc_id))
    doc_item.accepted += 1
    doc_item.last_user_id = registered_user.id
    doc_item.log_forward(datetime.now().strftime('%b %d, %G %I:%M %p'),remark)
    db.session.commit()
    flash('Forwarded document successfully')
    return redirect(url_for('index'))

@app.route('/close/<int:doc_id>',methods=['GET','POST'])
@login_required
@canclose
def close(doc_id):
    doc_item = Docs.query.get(doc_id)
    if request.method == 'GET':
        return render_template('close.html',doc=doc_item)
    remark = request.form['remark']
    doc_item.accepted = -1
    doc_item.log_forward(datetime.now().strftime('%b %d, %G %I:%M %p'),remark)
    db.session.commit()
    flash('Closed document successfully')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.before_request
def before_request():
    g.user = current_user

