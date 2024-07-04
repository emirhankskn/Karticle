from flask import g,Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
# from passlib.hash import sha256_crypt #USE WHEN YOU MAKE REGİSTER SECTION
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from datetime import datetime
import os

#BASİS ADJUSTMENTS
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/Emir/Desktop/Desktop/KarticleV3/karticlevtmain.db"
app.config["SECRET_KEY"] = "karticle_main"
ckeditor = CKEditor(app)

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)
#END OF BASİS ADJUSTMENTS


#DEFİNE CLASS FOR DATABASE
class Articles(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable = False)
    author = db.Column(db.String(25), nullable = False)
    content = db.Column(db.String(255), nullable = False)
    show_home = db.Column(db.Boolean, default = False)
    explore_content = db.Column(db.String(255), nullable = False)
    img_path = db.Column(db.String(255), nullable = False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)

class UserMessages(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(50), nullable = False)
    msg = db.Column(db.String(255), nullable = False)
#END OF DEFİNE CLASS FOR DATABASE



#LOGİN 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect(url_for("index"))
#END OF LOGİN 


#MAİN 
@app.route("/")
def index():
    articles = Articles.query.all()
    return render_template("index.html", articles = articles)
#END OF MAİN 


#EXPLORE 
@app.route("/explore")
def explore():
    articles = Articles.query.all()
    return render_template("explore.html", articles = articles)
#END OF EXPLORE 


#DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    articles = Articles.query.all()
    return render_template("dashboard.html", articles = articles)
#END OF DASHBOARD


#ADD ARTİCLE
@app.route("/addarticle", methods = ["GET", "POST"])
@login_required
def addarticle():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        explore_content = request.form.get("explore_content")
        show_home = request.form.get("show_home") == 'on'

        uploaded_file = request.files['file']

        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            newArticle = Articles(
                title = title,
                author = session.get('username'),
                content = content,
                show_home = show_home,
                explore_content = explore_content,
                img_path = file_path,
                created_date = datetime.utcnow()
            )
        db.session.add(newArticle)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template("addarticle.html")
#ADD ARTICLE END

#DELETE ARTICLE
@app.route('/delete/<string:ID>')
def deleteArticle(ID):
    article = Articles.query.get(ID)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for("dashboard"))
#DELETE ARTICLE END


#UPDATE ARTICLE
@app.route('/update/<string:ID>', methods = ["GET", "POST"])
def updateArticle(ID):
    article = Articles.query.get(ID)
    
    if request.method == "POST":
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.explore_content = request.form.get('explore_content')
        article.show_home = request.form.get('show_home') == 'on'

        uploaded_file = request.files['file']
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            article.img_path=file_path
        else: print("Error")
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('update.html', article = article)
#UPDATE ARTICLE END


#ARTICLE DETAIL
@app.route("/article/<string:ID>")
def articleDetail(ID):
    article = Articles.query.get(ID)
    return render_template("article.html", article = article)
#ARTICLE DETAIL END


#ABOUT
@app.route("/about")
def about():
    return render_template("about.html")
#ABOUT END

#CONTACT
@app.route("/contact", methods = ["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        msg = request.form.get('msg')

        sendMessage = UserMessages(name = name, email = email, msg = msg)
        db.session.add(sendMessage)
        db.session.commit()
        flash('Mesaj yazara iletildi', 'success')
        return render_template("contact.html")
    return render_template("contact.html")
#CONTACT END


#SHOW USER MESSAGES
@app.route("/usermessages")
def usermessages():
    user_messages = UserMessages.query.all()
    return render_template("usermessages.html", user_messages = user_messages)
#SHOW USER MESSAGES END


#DELETE USER MESSAGES
@app.route("/deleteusermessage/<string:ID>")
def deleteUserMessage(ID):
    deleteMessage = UserMessages.query.get(ID)
    if deleteMessage:
        db.session.delete(deleteMessage)
        db.session.commit()
        return redirect(url_for('usermessages'))
    else:
        return redirect(url_for('usermessages'))
#DELETE USER MESSAGES END


#SEARCH
@app.route('/search', methods = ["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form.get('keyword')
        results = Articles.query.filter(
            or_(
                Articles.title.ilike(f"%{keyword}%"),
                Articles.author.ilike(f"%{keyword}%"),
            )
        ).all()
        return render_template("explore.html", articles = results)
#SEARCH END


#FOR RUNNING APP AND DATABASE
with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug = True)
#FOR RUNNING APP AND DATABASE END

