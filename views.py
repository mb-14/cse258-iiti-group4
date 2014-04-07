from flask import session, request, flash, url_for, redirect, render_template, abort ,g
from app import app
from datetime import datetime
from models import *
from flask.ext.login import login_user , logout_user , current_user , login_required


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if g.user.is_authenticated():
        if request.method == 'POST':
            doc_id = request.form['accept']
            doc_item = Docs.query.get(doc_id)
            doc_item.accepted += 1
            doc_item.log_approve(g.user.department,datetime.now().strftime('%d/%m/%Y %H:%M'))
            db.session.commit()
            flash('Document accepted')
            redirect(url_for('index'))
        return render_template('index.html',docs=Docs.query.order_by(Docs.init_date.desc()).all(),current=g.user.id)
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
            doc = Docs(request.form['title'], request.form['amount'])
            doc.last_user_id = doc.user_id = g.user.id
            
            doc.log_approve(g.user.department,'NA')
            db.session.add(doc)
            db.session.commit()
            flash('Document was successfully created')
            return redirect(url_for('index'))
    return render_template('new.html')



@app.route('/doc/<int:doc_id>')
@login_required
def show(doc_id):
    doc_item = Docs.query.get(doc_id)
    return render_template('view.html',doc=doc_item,name=User.query.get(doc_item.user_id).username)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['username']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(username=username).first()
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
def forward(doc_id):
    doc_item = Docs.query.get(doc_id)
    if request.method == 'GET':
        return render_template('forward.html',doc=doc_item)
    
    recipient = request.form['recipient']
    remark = request.form['remark']
    registered_user = User.query.filter_by(email=recipient).first()
    if registered_user is None:
        flash('Recipient email ID does not exist' , 'error')
        return redirect(url_for('forward',doc_id=doc_id))
    doc_item.last_user_id = registered_user.id
    doc_item.accepted += 1
    doc_item.log_forward(datetime.now().strftime('%d/%m/%Y %H:%M'),remark)
    db.session.commit()
    flash('Forwarded document successfully')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) 

@app.before_request
def before_request():
    g.user = current_user

