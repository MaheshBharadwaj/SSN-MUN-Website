import hashlib
import os
import json
import time
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=ROOT_DIR + "/static/")
app.config["SECRET_KEY"] = "9OLWxND4o83j4K4iuopO"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


def generate_otp(email):
    return(str(int(hashlib.sha224(bytes(email, 'utf-8')).hexdigest()[-5:], 16)))


def check_password(user_password, password):
    return user_password == password


def get_committee(id: str):
    if id[0:2] == 'DI':
        return 'disec'
    elif id[0:2] == 'HR':
        return 'unhrc'
    elif id[0:2] == 'SC':
        return 'unsc'
    elif id[0:2] == 'EF':
        return 'ecofin'
    else:
        return 'eb'


committees = ['disec', 'unhrc', 'unsc', 'ecofin']
country_id = {}
for committee in committees:
    try:
        with open(ROOT_DIR+'/static/delegate_info/'+committee+'.json') as com_file:
            country_id[committee] = []

            com_json = json.load(com_file)
            for id in com_json.keys():
                country_id[committee].append(
                    {'id': id, 'country': com_json[id]['country']}
                )

        country_id[committee].sort(key=lambda x: x['country'])

    except Exception as e:
        print(e)
        break

# print(country_id['unhrc'])


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    country = db.Column(db.String(200))
    committee = db.Column(db.String(6))


db.create_all(app=app)

# try:
#     new_user = User(
#         id="ADMIN432",
#         email="maheshbharadwaj134511819124129@cse.ssn.edu.in",
#         name="Pritham",
#         password=generate_password_hash("admin@ssn", method="sha256"),
#     )

#     with app.app_context():
#         # add the new user to the database
#         db.session.add(new_user)
#         db.session.commit()
#         print("added user")
# except Exception as e:
#     print(e)


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
    if not user or not check_password(user.password, password):
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

    # recv_json = os.path.join('messages/pogchamps/recv.json')
    # sent_json = os.path.join('messages/pogchamps/sent.json')
    # recv_file = open(recv_json)
    # sent_file = open(sent_json)
    # recv = json.load(recv_file)
    # sent = json.load(sent_file)

    # print(recv)
    # print(sent)

    # recv_file.close()
    # sent_file.close()

    # now = datetime.now()

    # timestamp = datetime.timestamp(now)

    bruh_object = {"message": "Hello there, fellow delegate!"}

    # print(bruh_object)
    # with open('messages/pogchamps/recv.json', 'r') as openfile:
    #     json_object = json.load(openfile)

    # json_object[timestamp] = bruh_object
    # print(json_object)
    # print(type(json_object))

    # json_object = json.dumps(json_object)
    # print(json_object)

    # # with open("messages/pogchamps/recv.json", "w") as outfile:
    # #     outfile.write(json_object)

    if current_user.id[2:] == 'EB':
        return render_template("eb-dashboard.html", name=current_user.name)
    return render_template("dashboard.html", name=current_user.name, recv_length=1, sent_length=1)


@app.route('/send-delegate', methods=['GET', 'POST'])
@login_required
def send_delegate():
    # checking and displaying approriately for GET request
    if request.method == 'GET':
        return render_template("delegate-message.html", mapper=country_id[get_committee(current_user.id)], eb_flag=(current_user.id[2:] == 'EB'))

    # getting all info from the submitted form
    form = request.form
    recv_delegate_id, recv_delegate_country = tuple(
        form['recv-selected'].split(';'))
    send_delegate_id, send_delegate_country = current_user.id, current_user.country
    message = form['chit-message']
    try:
        to_eb = True if form['to-eb-check'] == 'on' else False
    except:
        to_eb = False

    # the message object itself
    message_obj = {
        'send-del-id': send_delegate_id,
        'send-del-country': send_delegate_country,
        'recv-del-id': recv_delegate_id,
        'recv-del-country': recv_delegate_country,
        'message': message,
        'timestamp': time.time(),
        'to-eb': to_eb
    }

    # writing to eb file if to-eb is true
    if message_obj['to-eb']:

        send_eb_json_path = ROOT_DIR + \
            f"/messages/{send_delegate_id[:2]}/EB/recv.json"

        with open(send_eb_json_path, 'r') as sender_file:
            data = json.load(sender_file)
            data.append(message_obj)

        with open(send_eb_json_path, 'w') as sender_file:
            json.dump(data, sender_file, indent=2)

    send_json_path = ROOT_DIR + \
        f"/messages/{send_delegate_id[:2]}/{send_delegate_id[2:]}/sent.json"
    recv_json_path = ROOT_DIR + \
        f"/messages/{recv_delegate_id[:2]}/{recv_delegate_id[2:]}/recv.json"
    with open(send_json_path, 'r') as sender_file:
        data = json.load(sender_file)
        data.append(message_obj)
    with open(send_json_path, 'w') as sender_file:
        json.dump(data, sender_file, indent=2)
    with open(recv_json_path, 'r') as receiver_file:
        data = json.load(receiver_file)
        data.append(message_obj)
    with open(recv_json_path, 'w') as receiver_file:
        json.dump(data, receiver_file, indent=2)
    return redirect("dashboard")


@app.route('/send-eb', methods=['GET', 'POST'])
@login_required
def send_eb():
    if request.method == 'GET':
        return render_template("eb-message.html")

    # getting all info from the submitted form
    form = request.form
    recv_delegate_id, recv_delegate_country = f'{current_user.id[:2]}EB', "Executive Board"
    send_delegate_id, send_delegate_country = current_user.id, current_user.country
    message = form['chit-message']
    to_eb = False

    # the message object itself
    message_obj = {
        'send-del-id': send_delegate_id,
        'send-del-country': send_delegate_country,
        'recv-del-id': recv_delegate_id,
        'recv-del-country': recv_delegate_country,
        'timestamp': time.time(),
        'message': message,
        'to-eb': to_eb
    }

    # writing to eb file if to-eb is true

    send_json_path = ROOT_DIR + \
        f"/messages/{send_delegate_id[:2]}/{send_delegate_id[2:]}/sent.json"
    recv_json_path = ROOT_DIR + \
        f"/messages/{recv_delegate_id[:2]}/{recv_delegate_id[2:]}/recv.json"
    with open(send_json_path, 'r') as sender_file:
        data = json.load(sender_file)
        data.append(message_obj)
    with open(send_json_path, 'w') as sender_file:
        json.dump(data, sender_file, indent=2)
    with open(recv_json_path, 'r') as receiver_file:
        data = json.load(receiver_file)
        data.append(message_obj)
    with open(recv_json_path, 'w') as receiver_file:
        json.dump(data, receiver_file, indent=2)

    return redirect(url_for('dashboard'))


@app.route('/sent-messages/<garbage>')
@login_required
def get_sent_message(garbage):
    regid = current_user.id
    com = regid[:2]
    folder = regid[2:]

    return send_file(ROOT_DIR+'/messages/'+com+'/'+folder+'/sent.json')


@app.route('/recv-messages/<garbage>')
@login_required
def get_recv_message(garbage):
    regid = current_user.id
    com = regid[:2]
    folder = regid[2:]

    return send_file(ROOT_DIR+'/messages/'+com+'/'+folder+'/recv.json')


if __name__ == "__main__":
    app.run(debug=True)
