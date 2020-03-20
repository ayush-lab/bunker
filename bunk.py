from flask import Flask,redirect,url_for,flash,render_template,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager,UserMixin, login_user, login_required,logout_user, current_user
from datetime import datetime
from markupsafe import escape
app = Flask(__name__)

app.config[' SQLAlCHEMY_TRACK_MODIFICATIONS '] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SECRET_KEY'] = "bunker_app_security_123456"

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
    #email = db.Column(db.String(80), unique=False)  # only until we are on development server
    #about_me = db.Column(db.String(140))
    #last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #posts = db.relationship('Post', backref='author', lazy='dynamic')  # relationship 1 btw post and user

    followed = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id),secondaryjoin=(followers.c.followed_id==id),
		backref=db.backref('followers',lazy='dynamic'), lazy='dynamic')  #relationship 2 btw user and followers

    time = db.relationship("Timetable",backref="OP", lazy ="dynamic")

    def bunk_matches(self):
    	bunker=Timetable.query.join(followers,(followers.c.followed_id==Timetable.OP_id)).filter(followers.c.follower_id ==self.id)
    	importance = Timetable.query.filter_by(priority="low" or "med")
    	return bunker.intersect(importance) 

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
	day= db.Column(db.String, unique=False)
	period_no =db.Column(db.Integer, unique=False)
	subject =db.Column(db.String,unique=False)
	priority =db.Column(db.String,unique=False)
	OP_id =db.Column(db.Integer,db.ForeignKey("user.id"))



from forms import loginForm, registerForm,PostForm,Timetableform
# timestamp=db.Column(db.DateTime, index=True, default=datetime.utcnow)
# user_id= db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route("/home")

def home():
	return render_template("index1.html")


@app.route("/logout")
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
    #form = loginForm()
    #if form.validate_on_submit():
    if request.method ="POST":
        user= User.query.filter_by(username=request.form["username"]).first()

        if user:
            if check_password_hash(user.password,request.form["password"]):
                login_user(user)
                return redirect(url_for("dashboard"))

                next_page = request.args.get('next')

                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('dashboard')

                return redirect(next_page)


        flash("invalid username or password")
        return redirect(url_for("login1"))

    return render_template("login.html",title="Login",form=form)

@app.route("/dashboard",methods=["POST","GET"])
@app.route("/dashboard/",methods=["POST","GET"])
@login_required

def dashboard():
	form=Timetableform()
	if form.validate_on_submit():
		print("a")
		x=Timetable(username=current_user.username,day="Monday",period_no=form.period11.data,subject=form.sub11.data,priority=form.importance11.data, OP=current_user)
		y=Timetable(username=current_user.username,day=form.day1.data,period_no=form.period12.data,subject=form.sub12.data,priority=form.importance12.data, OP=current_user)
		j =Timetable(username=current_user.username,day=form.day2.data, period_no=form.period21.data,subject=form.sub21.data,priority=form.importance21.data,OP=current_user)
		db.session.add(x)
		db.session.add(y)
		db.session.add(j)
		db.session.commit()


		flash("thanks for filling up the informations!")
		return redirect(url_for("timetable"))

	return render_template("dashboard.html", form=form)

@app.route("/timetable")
@login_required
def timetable():
	user = Timetable.query.filter_by(username=current_user.username).all()
	return render_template("timetable.html",user=user)


@app.route("/<day>/<int:period>",methods=["POST","GET"])
#@app.route("<day>/<int::period>",methods=["POST","GET"])
#@app.route("/bunkdex/",methods=["POST","GET"])
@login_required
def bunkdex(day,period):
	#querym=matches().query.filter_by(day =day).filter_by(period=period).all()
	querym = current_user.bunk_matches().filter_by(day=day,period_no=period).all()
    


	return render_template("bunkdex.html", title="bunkdex", querym=querym)


@app.route("/profile/<username>")
@login_required
def profile(username):
	user=User.query.filter_by(username=username).first_or_404()

	return render_template("profile.html",user=user)



@app.route("/edit_timetable")
@login_required
def edit_profile():
	render_template("edit_profile.html")

@app.route('/follow/<username>')
@login_required
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for("timetable"))
	if user == current_user:
		flash('you cant follow yourself.')
		return redirect(url_for('.avatar', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('you have followed {}!'.format(username))
	#return redirect(url_for('.avatar', username=username))
	return redirect(url_for("timetable"))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for("timetable"))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('.avatar', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You have unfollowed {}.'.format(username))
	return redirect(url_for('.avatar', username=username))