import hashlib
import os
import json
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=ROOT_DIR + "/static/")
app.config["SECRET_KEY"] = "9OLWxND4o83j4K4iuopO"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

# format for JSON message object
# messageid {
#     reciever or sender:
#     message: content
# }


db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


db.create_all(app=app)

try:
    new_user = User(
        id="ADMIN3",
        email="maheshbharadwaj18199@cse.ssn.edu.in",
        name="Pritham",
        password=generate_password_hash("admin@ssn", method="sha256"),
    )

    with app.app_context():
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        print("added user")
except:
    pass


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(user_id)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    regid = request.form.get("regid")
    password = request.form.get("password")
    remember = True  # if request.form.get('remember') else False
    print("regid: %s\tpass: %s" % (regid, password))
    user = User.query.filter_by(id=regid).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        # if user doesn't exist or password is wrong, reload the page
        return redirect(url_for("login"))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("dashboard"))


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    # need to read how many sent messages there are.

    recv_json = os.path.join('messages/pogchamps/recv.json')
    sent_json = os.path.join('messages/pogchamps/sent.json')
    recv_file = open(recv_json)
    sent_file = open(sent_json)
    recv = json.load(recv_file)
    sent = json.load(sent_file)

    # print(recv)
    # print(sent)

    # recv_file.close()
    # sent_file.close()

    # now = datetime.now()

    # timestamp = datetime.timestamp(now)
    
    # bruh_object = {"message": "Hello there, fellow delegate!"}

    # # print(bruh_object)
    # with open('messages/pogchamps/recv.json', 'r') as openfile:
    #     json_object = json.load(openfile)
        
    # json_object[timestamp] = bruh_object
    # print(json_object) 
    # print(type(json_object)) 

    # json_object = json.dumps(json_object)
    # print(json_object)

    # with open("messages/pogchamps/recv.json", "w") as outfile: 
    #     outfile.write(json_object)

    return render_template("dashboard.html", name=current_user.name, recv_length = len(recv), sent_length = len(sent))


@app.route('/send-delegate', methods=['GET', 'POST'])
@login_required
def send_delegate():
    if request.method == 'GET':
        return render_template("delegate-message.html")
    elif request.method == 'POST':
        print(request.form)
        return render_template("dashboard.html")

    return redirect(url_for('dashboard'))


@app.route('/send-eb', methods=['GET', 'POST'])
@login_required
def send_eb():
    if request.method == 'GET':
        return render_template("eb-message.html")

    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
