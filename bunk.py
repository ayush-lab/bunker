from flask import Flask,redirect,url_for,flash,render_template,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager,UserMixin, login_user, login_required,logout_user, current_user
from datetime import datetime
from markupsafe import escape
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os
from datetime import date
from random import random 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}
app.config[' SQLAlCHEMY_TRACK_MODIFICATIONS '] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SECRET_KEY'] = "bunker_app_security_123456"
app.config["UPLOAD_FOLDER"] = basedir + "/static/img"

test= basedir + "/static/img"

db = SQLAlchemy(app)
migrate = Migrate(app,db)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'          # LOGINMANAGER
login_manager.login_message = " Please, login first to access "

@login_manager.user_loader                #important
def load_user(id):
	return User.query.get(int(id))


followers = db.Table('followers', db.Column('follower_id', db.Integer,db.ForeignKey('user.id')), 
								  db.Column('followed_id', db.Integer,db.ForeignKey('user.id')) )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80), unique=True)
    profile_pic=db.Column(db.String(50),nullable=False,default="img/default.jpeg")
    #email = db.Column(db.String(80), unique=False)  # only until we are on development server
    about_me = db.Column(db.String(140))
    college= db.Column(db.String(40), default = "Ajay kumar Garg engineering college")
    #last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    #posts = db.relationship('Post', backref='author', lazy='dynamic')  # relationship 1 btw post and user

    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id),secondaryjoin=(followers.c.followed_id==id),
		backref=db.backref('followers',lazy='dynamic'), lazy='dynamic')  #relationship 2 btw user and followers

    time = db.relationship("Timetable",backref="OP", lazy ="dynamic")

    def bunk_matches(self):
    	bunker=Timetable.query.join(followers,(followers.c.followed_id==Timetable.OP_id)).filter(followers.c.follower_id ==self.id)
    	importance1 = Timetable.query.filter_by(priority= "M")
    	importance2 = Timetable.query.filter_by(priority= "H")
    	return bunker.intersect(importance1).union(importance2) 

    def follow(self,user):
    	if not self.is_following(user):
    		self.followed.append(user)

    def unfollow(self,user):
    	if self.is_following(user):
    		self.followed.remove(user)
    def is_following(self,user):
    	return self.followed.filter(followers.c.followed_id==user.id).count()>0


'''class Post(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	body= db.Column(db.String(140))
	timestamp=db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id= db.Column(db.Integer, db.ForeignKey('user.id'))'''

class Timetable(UserMixin,db.Model):
	id= db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=False)
	day= db.Column(db.String, unique=False, nullable=True)
	period_no =db.Column(db.Integer, unique=False, nullable=False,default="None")
	subject =db.Column(db.String,unique=False, nullable=False, default="None")
	priority =db.Column(db.String,unique=False, nullable=False, default="None")
	OP_id =db.Column(db.Integer,db.ForeignKey("user.id"))



from forms import loginForm, registerForm,PostForm,Timetableform
# timestamp=db.Column(db.DateTime, index=True, default=datetime.utcnow)
# user_id= db.Column(db.Integer, db.ForeignKey('user.id'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route("/logout")
@app.route("/logout/")
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))

@app.route("/signup",methods=["POST","GET"])
@app.route("/signup/",methods=["POST","GET"])

def signup():
    if current_user.is_authenticated:
        return redirect(url_for("login"))
    #form = registerForm()
    #if form.validate_on_submit():
    if request.method == "POST":
    	print("done")
    	new_user=User(username=request.form["username"],password=generate_password_hash(request.form["password"]))
    	db.session.add(new_user)
    	db.session.commit()

    	return redirect(url_for("login"))
    return render_template("signup1.html")


@app.route("/login",methods=["POST","GET"])
@app.route("/login/",methods=["POST","GET"])
def login():
	if request.method == "POST":
		print("a")
		user= User.query.filter_by(username=request.form["username"]).first()
		if user:
			if check_password_hash(user.password,request.form["password"]):
				login_user(user)
				print("a")
				return redirect(url_for("dashboard"))
				next_page = request.args.get('next')
				if not next_page or url_parse(next_page).netloc != '':
					next_page = url_for('dashboard')

					return redirect(next_page)
			return redirect(url_for("login"))
	return render_template("login1.html",title="Login")


@app.route("/dashboard",methods=["POST","GET"])
@app.route("/dashboard/",methods=["POST","GET"])
@login_required

def dashboard():
	if request.method == 'POST':
		print("aaaaa")

		x=Timetable(username=current_user.username,day="Monday",period_no=1, OP=current_user)
		current_user.time[0].subject=request.form["sub11"]
		current_user.time[0].priority=request.form["imp11"]
		db.session.add(x)
		print("okkkk")

		x=Timetable(username=current_user.username,day="Monday",period_no=2,OP=current_user)
		current_user.time[1].subject=request.form["sub12"]
		current_user.time[1].priority=request.form["imp12"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=3,OP=current_user)
		current_user.time[2].subject=request.form["sub13"]
		current_user.time[2].priority=request.form["imp13"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=4, OP=current_user)
		current_user.time[3].subject=request.form["sub14"]
		current_user.time[3].priority=request.form["imp14"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=5, OP=current_user)
		current_user.time[4].subject=request.form["sub15"]
		current_user.time[4].priority=request.form["imp15"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=6, OP=current_user)
		current_user.time[5].subject=request.form["sub16"]
		current_user.time[5].priority=request.form["imp16"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=7, OP=current_user)
		current_user.time[6].subject=request.form["sub17"]
		current_user.time[6].priority=request.form["imp17"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=8, OP=current_user)
		current_user.time[7].subject=request.form["sub18"]
		current_user.time[7].priority=request.form["imp18"]
		db.session.add(x)


		print('second stage')
		x=Timetable(username=current_user.username,day="Tuesday",period_no=1, OP=current_user)
		current_user.time[8].subject=request.form["sub21"]
		current_user.time[8].priority=request.form["imp21"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=2,OP=current_user)
		current_user.time[9].subject=request.form["sub22"]
		current_user.time[9].priority=request.form["imp22"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=3,OP=current_user)
		current_user.time[10].subject=request.form["sub23"]
		current_user.time[10].priority=request.form["imp23"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=4, OP=current_user)
		current_user.time[11].subject=request.form["sub24"]
		current_user.time[11].priority=request.form["imp24"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=5, OP=current_user)
		current_user.time[12].subject=request.form["sub25"]
		current_user.time[12].priority=request.form["imp25"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=6, OP=current_user)
		current_user.time[13].subject=request.form["sub26"]
		current_user.time[13].priority=request.form["imp26"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=7, OP=current_user)
		current_user.time[14].subject=request.form["sub27"]
		current_user.time[14].priority=request.form["imp27"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=8, OP=current_user)
		current_user.time[15].subject=request.form["sub28"]
		current_user.time[15].priority=request.form["imp28"]
		db.session.add(x)



		print('second stage')
		x=Timetable(username=current_user.username,day="Wednesday",period_no=1, OP=current_user)
		current_user.time[16].subject=request.form["sub31"]
		current_user.time[16].priority=request.form["imp31"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=2, OP=current_user)
		current_user.time[17].subject=request.form["sub32"]
		current_user.time[17].priority=request.form["imp32"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=3, OP=current_user)
		current_user.time[18].subject=request.form["sub33"]
		current_user.time[18].priority=request.form["imp33"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=4, OP=current_user)
		current_user.time[19].subject=request.form["sub34"]
		current_user.time[19].priority=request.form["imp34"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=5, OP=current_user)
		current_user.time[20].subject=request.form["sub35"]
		current_user.time[20].priority=request.form["imp35"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=6, OP=current_user)
		current_user.time[21].subject=request.form["sub36"]
		current_user.time[21].priority=request.form["imp36"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=7, OP=current_user)
		current_user.time[22].subject=request.form["sub37"]
		current_user.time[22].priority=request.form["imp37"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=8, OP=current_user)
		current_user.time[23].subject=request.form["sub38"]
		current_user.time[23].priority=request.form["imp38"]
		db.session.add(x)
		print('second stage')

		x=Timetable(username=current_user.username,day="Thursday",period_no=1,OP=current_user)
		current_user.time[24].subject=request.form["sub41"]
		current_user.time[24].priority=request.form["imp41"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=2, OP=current_user)
		current_user.time[25].subject=request.form["sub42"]
		current_user.time[25].priority=request.form["imp42"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=3, OP=current_user)
		current_user.time[26].subject=request.form["sub43"]
		current_user.time[26].priority=request.form["imp43"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=4, OP=current_user)
		current_user.time[27].subject=request.form["sub44"]
		current_user.time[27].priority=request.form["imp44"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=5, OP=current_user)
		current_user.time[28].subject=request.form["sub45"]
		current_user.time[28].priority=request.form["imp45"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=6, OP=current_user)
		current_user.time[29].subject=request.form["sub46"]
		current_user.time[29].priority=request.form["imp46"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=7, OP=current_user)
		current_user.time[30].subject=request.form["sub47"]
		current_user.time[30].priority=request.form["imp47"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=8, OP=current_user)
		current_user.time[31].subject=request.form["sub48"]
		current_user.time[31].priority=request.form["imp48"]
		db.session.add(x)

		print('second stage')
		x=Timetable(username=current_user.username,day="Friday",period_no=1, OP=current_user)
		current_user.time[32].subject=request.form["sub51"]
		current_user.time[32].priority=request.form["imp51"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=2, OP=current_user)
		current_user.time[33].subject=request.form["sub52"]
		current_user.time[33].priority=request.form["imp52"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=3, OP=current_user)
		current_user.time[34].subject=request.form["sub53"]
		current_user.time[34].priority=request.form["imp53"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=4, OP=current_user)
		current_user.time[35].subject=request.form["sub54"]
		current_user.time[35].priority=request.form["imp54"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=5, OP=current_user)
		current_user.time[36].subject=request.form["sub55"]
		current_user.time[36].priority=request.form["imp55"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=6, OP=current_user)
		current_user.time[37].subject=request.form["sub56"]
		current_user.time[37].priority=request.form["imp56"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=7,OP=current_user)
		current_user.time[38].subject=request.form["sub57"]
		current_user.time[38].priority=request.form["imp57"]
		db.session.add(x)
		print("omg")
		x=Timetable(username=current_user.username,day="Friday",period_no=8, OP=current_user)
		current_user.time[39].subject=request.form["sub58"]
		current_user.time[39].priority=request.form["imp58"]
		db.session.add(x)
		print("done")
		db.session.commit()

		return redirect(url_for('home'))

	return render_template("form.html")


@app.route("/editboard",methods=["POST","GET"])
@app.route("/editboard/",methods=["POST","GET"])
@login_required

def editboard():
	if request.method == 'POST':
		print("aaaaa")

		x=Timetable(username=current_user.username,day="Monday",period_no=1, OP=current_user)
		current_user.time[0].subject=request.form["sub11"]
		current_user.time[0].priority=request.form["imp11"]
		db.session.add(x)
		print("okkkk")

		x=Timetable(username=current_user.username,day="Monday",period_no=2,OP=current_user)
		current_user.time[1].subject=request.form["sub12"]
		current_user.time[1].priority=request.form["imp12"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=3,OP=current_user)
		current_user.time[2].subject=request.form["sub13"]
		current_user.time[2].priority=request.form["imp13"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=4, OP=current_user)
		current_user.time[3].subject=request.form["sub14"]
		current_user.time[3].priority=request.form["imp14"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=5, OP=current_user)
		current_user.time[4].subject=request.form["sub15"]
		current_user.time[4].priority=request.form["imp15"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=6, OP=current_user)
		current_user.time[5].subject=request.form["sub16"]
		current_user.time[5].priority=request.form["imp16"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=7, OP=current_user)
		current_user.time[6].subject=request.form["sub17"]
		current_user.time[6].priority=request.form["imp17"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Monday",period_no=8, OP=current_user)
		current_user.time[7].subject=request.form["sub18"]
		current_user.time[7].priority=request.form["imp18"]
		db.session.add(x)


		print('second stage')
		x=Timetable(username=current_user.username,day="Tuesday",period_no=1, OP=current_user)
		current_user.time[8].subject=request.form["sub21"]
		current_user.time[8].priority=request.form["imp21"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=2,OP=current_user)
		current_user.time[9].subject=request.form["sub22"]
		current_user.time[9].priority=request.form["imp22"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=3,OP=current_user)
		current_user.time[10].subject=request.form["sub23"]
		current_user.time[10].priority=request.form["imp23"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=4, OP=current_user)
		current_user.time[11].subject=request.form["sub24"]
		current_user.time[11].priority=request.form["imp24"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=5, OP=current_user)
		current_user.time[12].subject=request.form["sub25"]
		current_user.time[12].priority=request.form["imp25"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=6, OP=current_user)
		current_user.time[13].subject=request.form["sub26"]
		current_user.time[13].priority=request.form["imp26"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=7, OP=current_user)
		current_user.time[14].subject=request.form["sub27"]
		current_user.time[14].priority=request.form["imp27"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Tuesday",period_no=8, OP=current_user)
		current_user.time[15].subject=request.form["sub28"]
		current_user.time[15].priority=request.form["imp28"]
		db.session.add(x)



		print('second stage')
		x=Timetable(username=current_user.username,day="Wednesday",period_no=1, OP=current_user)
		current_user.time[16].subject=request.form["sub31"]
		current_user.time[16].priority=request.form["imp31"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=2, OP=current_user)
		current_user.time[17].subject=request.form["sub32"]
		current_user.time[17].priority=request.form["imp32"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=3, OP=current_user)
		current_user.time[18].subject=request.form["sub33"]
		current_user.time[18].priority=request.form["imp33"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=4, OP=current_user)
		current_user.time[19].subject=request.form["sub34"]
		current_user.time[19].priority=request.form["imp34"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=5, OP=current_user)
		current_user.time[20].subject=request.form["sub35"]
		current_user.time[20].priority=request.form["imp35"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=6, OP=current_user)
		current_user.time[21].subject=request.form["sub36"]
		current_user.time[21].priority=request.form["imp36"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=7, OP=current_user)
		current_user.time[22].subject=request.form["sub37"]
		current_user.time[22].priority=request.form["imp37"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Wednesday",period_no=8, OP=current_user)
		current_user.time[23].subject=request.form["sub38"]
		current_user.time[23].priority=request.form["imp38"]
		db.session.add(x)
		print('second stage')

		x=Timetable(username=current_user.username,day="Thursday",period_no=1,OP=current_user)
		current_user.time[24].subject=request.form["sub41"]
		current_user.time[24].priority=request.form["imp41"] 
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=2, OP=current_user)
		current_user.time[25].subject=request.form["sub42"]
		current_user.time[25].priority=request.form["imp42"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=3, OP=current_user)
		current_user.time[26].subject=request.form["sub43"]
		current_user.time[26].priority=request.form["imp43"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=4, OP=current_user)
		current_user.time[27].subject=request.form["sub44"]
		current_user.time[27].priority=request.form["imp44"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=5, OP=current_user)
		current_user.time[28].subject=request.form["sub45"]
		current_user.time[28].priority=request.form["imp45"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=6, OP=current_user)
		current_user.time[29].subject=request.form["sub46"]
		current_user.time[29].priority=request.form["imp46"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=7, OP=current_user)
		current_user.time[30].subject=request.form["sub47"]
		current_user.time[30].priority=request.form["imp47"]
		db.session.add(x)
		x=Timetable(username=current_user.username,day="Thursday",period_no=8, OP=current_user)
		current_user.time[31].subject=request.form["sub48"]
		current_user.time[31].priority=request.form["imp48"]
		db.session.add(x)

		print('second stage')
		x=Timetable(username=current_user.username,day="Friday",period_no=1, OP=current_user)
		current_user.time[32].subject=request.form["sub51"]
		current_user.time[32].priority=request.form["imp51"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=2, OP=current_user)
		current_user.time[33].subject=request.form["sub52"]
		current_user.time[33].priority=request.form["imp52"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=3, OP=current_user)
		current_user.time[34].subject=request.form["sub53"]
		current_user.time[34].priority=request.form["imp53"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=4, OP=current_user)
		current_user.time[35].subject=request.form["sub54"]
		current_user.time[35].priority=request.form["imp54"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=5, OP=current_user)
		current_user.time[36].subject=request.form["sub55"]
		current_user.time[36].priority=request.form["imp55"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=6, OP=current_user)
		current_user.time[37].subject=request.form["sub56"]
		current_user.time[37].priority=request.form["imp56"]
		db.session.add(x)
		print("what")
		x=Timetable(username=current_user.username,day="Friday",period_no=7,OP=current_user)
		current_user.time[38].subject=request.form["sub57"]
		current_user.time[38].priority=request.form["imp57"]
		db.session.add(x)
		print("omg")
		x=Timetable(username=current_user.username,day="Friday",period_no=8, OP=current_user)
		current_user.time[39].subject=request.form["sub58"]
		current_user.time[39].priority=request.form["imp58"]
		db.session.add(x)
		print("done")
		db.session.commit()

		return redirect(url_for('home'))

	return render_template("form_edit.html")

@app.route("/home")
@app.route("/home/")
@login_required
def home():
	user = Timetable.query.filter_by(username=current_user.username).all()
	return render_template("index (4).html",user=user)


@app.route("/<day>/<int:period>",methods=["POST","GET"])
#@app.route("<day>/<int::period>",methods=["POST","GET"])
#@app.route("/bunkdex/",methods=["POST","GET"])
@login_required
def bunkdex(day,period):
	#querym=matches().query.filter_by(day =day).filter_by(period=period).all()
	query = current_user.bunk_matches().filter_by(day=day,period_no=period).all()



	return render_template("table.html", title="bunkdex", query=query)	

@app.route("/profile/<username>", methods=["GET","POST"])
@app.route("/profile/<username>/", methods=["GET","POST"])
@login_required
def profile(username):
	

	'''if request.method == 'POST': 

		if 'file' not in request.files:
		
			return url_for(request.url)
			
		file=request.files['file']
		if file.filename == "":
			return url_for(request.url)

		if file and allowed_file(file.filename):
		
			filename =secure_filename(file.filename)
			filename= str(date.today()) + str(random() ) + filename 
			user_pic = "img/" + filename
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			current_user.profile_pic = user_pic
			db.session.commit()
		else:
			'''
	user = Timetable.query.filter_by(username=current_user.username).all()
	u=User.query.filter_by(username=username).first_or_404()
	img_scr=url_for('static', filename= u.profile_pic) 
	return render_template("user_profile.html",user=user, img_scr=img_scr,u=u) 



@app.route("/edit_profile/<username>",methods=["POST","GET"])
@login_required
def edit_profile(username):
	if request.method == "POST":
		current_user.username=request.form["username"]
		for name in range(40):
			current_user.time[name].username=request.form["username"]

		current_user.college=request.form["college"]
		current_user.about_me=request.form["status"]
		db.session.commit()
		if 'file' in request.files:

			file=request.files['file']
			if file.filename == "":
				return url_for(request.url)

			if file and allowed_file(file.filename):
			
				filename =secure_filename(file.filename)
				filename= str(date.today()) + str(random() ) + filename 
				user_pic = "img/" + filename
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				current_user.profile_pic = user_pic
				db.session.commit()
				return redirect(url_for('.profile', username=request.form["username"]))
			else:
				return '''<p> this file is not allowed <p>''' 
		else:
			return redirect(url_for('.profile', username=request.form["username"]))


	user=User.query.filter_by(username=username).first()
	img_scr=url_for('static', filename= current_user.profile_pic)
	return render_template("edit_profile.html",img_scr=img_scr,user=user  )	
	
'''	elif request.method =="GET":

		request.form["username"] =current_user.username
		request.form["status"] = current_user.about_me
		request.form["college"] =current_user.college '''

	
	


@app.route('/follow/<username>')
@app.route('/follow/<username>/')

@login_required
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		return ''' user not found'''
		return redirect(url_for("home"))
	if user == current_user:
		

		return redirect(url_for('.profile', username=username))

	current_user.follow(user)
	db.session.commit()
	#flash('you have followed {}!'.format(username))
	#return redirect(url_for('.avatar', username=username))
	return redirect(url_for('.profile', username=username))

@app.route('/unfollow/<username>')
@app.route('/unfollow/<username>/')

@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		return ''' user not found'''
		
	if user == current_user:
		
		return redirect(url_for('.profile', username=username))
	current_user.unfollow(user)
	db.session.commit()
	#flash('You have unfollowed {}.'.format(username))
	return redirect(url_for('.profile', username=username))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/index")
@app.route("/index/")
def index():
	return render_template("index1.html")

if __name__ == '__main__':
	app.run()