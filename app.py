import hashlib
import os
import json
import copy
import random
import time
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, send_from_directory
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from quickstart import quickstart
from generate_sheet import generate_sheet

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


def authors_shuffle():
    authors = [{'name': 'Mahesh', 'github': "https://github.com/maheshbharadwaj"}, {'name': 'Vanathi', 'github': "https://github.com/vanathi-g"},
               {'name': 'Dhiganth', 'github': "https://github.com/dhiganthrao"}, {'name': 'Pritham', 'github': "https://github.com/prithamimmanuel"}]
    random.shuffle(authors)
    return(authors)


# secratariat.json has the info that we need to display on the about us page cards
member_file_name = os.path.join(app.static_folder, "js", "secratariat.json")
member_file = open(member_file_name)
members = json.load(member_file)

# executive_board.json has info about eb members
member_file_name = os.path.join(
    app.static_folder, "js", "executive_board.json")
eb_member_file = open(member_file_name)
eb_members = json.load(eb_member_file)

# committees.json has required info about commitees - url, name, agenda
comm_file_name = os.path.join(app.static_folder, "js", "committees.json")
comm_file = open(comm_file_name)
committees = json.load(comm_file)


committees_list = ['disec', 'unhrc', 'unsc', 'ecofin']
country_id = {}
for committee in committees_list:
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
quickstart()


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(user_id)


@app.errorhandler(404)
def not_found(e):

    return render_template("404.html"), 404


@app.route("/", methods=["GET"])
def index():

    if request.method == "GET":
        comm_copy = [copy.deepcopy(x) for x in committees]
        for committee_obj in comm_copy:
            committee_obj["img"] = url_for(
                "static", filename=committee_obj["img"])
        return render_template(
            "index.html", page_title="SSN MUN 2021", committees=comm_copy, authors=authors_shuffle()
        )


@app.route("/organising-committee", methods=["GET"])
def organising_committee():

    if request.method == "GET":
        # creating copy to avoid modifying original info - fixes images disappearing on refresh issue
        members_copy = [copy.deepcopy(x) for x in members]

        for member in members_copy:
            member["img"] = url_for("static", filename=member["img"])
        return render_template(
            "organising_committee.html",
            members=members_copy,
            page_title="Organising Committee", authors=authors_shuffle()
        )


@app.route("/committee/<commname>", methods=["GET"])
def committee(commname):
    display_committee = None
    # Figure out which committe info to display
    for committee in committees:
        if committee["url"] == commname:
            display_committee = committee

    if display_committee is None:
        return render_template('404.html'), 404

    # Only get info about EB members for required committee
    comm_eb = [x for x in eb_members if x["committee"] == commname]
    comm_eb_copy = [copy.deepcopy(x) for x in comm_eb]
    for eb_member in comm_eb_copy:
        eb_member["img"] = url_for("static", filename=eb_member["img"])

    if request.method == "GET":
        return render_template(
            "committee.html",
            committee=display_committee,
            members=comm_eb_copy,
            page_title=commname.upper(), authors=authors_shuffle()
        )


@app.route("/about", methods=["GET"])
def about():

    if request.method == "GET":
        return render_template("about.html", page_title="About Us", authors=authors_shuffle())


@app.route("/sponsors", methods=["GET"])
def sponsors():

    if request.method == "GET":
        return render_template("sponsors.html", page_title="Sponsors", authors=authors_shuffle())


@app.route("/registrations", methods=["GET"])
@app.route("/registrations/<type>", methods=["GET"])
def registrations(type=None):

    if type == "delegate":
        return render_template(
            "registration_form.html",
            page_title="Delegate Registration",
            doc_link="https://docs.google.com/forms/d/e/1FAIpQLScoxoetemZQHqdBEtq_b6eIZhJdiS3cCsWhgevDgQC59TowhQ/viewform?embedded=true", authors=authors_shuffle()
        )
    elif type == "ip":
        return render_template(
            "registration_form.html",
            page_title="IP Registration",

            doc_link="https://docs.google.com/forms/d/e/1FAIpQLSclGtGrtRtdCpWyV9P6KRxRkX2pqjCmYRwdA88JaKMhcwhaBQ/viewform?embedded=true", authors=authors_shuffle()
        )
    # elif type == 'eb':
    #     return render_template('registration_form.html', page_title='EB Registration', doc_link="https://docs.google.com/forms/d/e/1FAIpQLSfAmJ62D7SHiKNAsJzO1iIkYfSEqpoYLyvdJ0xCuvnSG-2xfg/viewform?embedded=true")
    else:
        return render_template("registrations.html", page_title="Registrations", authors=authors_shuffle())


@app.route("/background-guides/<committee>", methods=["GET"])
def background_guides(committee):

    return send_from_directory(
        ROOT_DIR + "/static/background_guides", committee + ".pdf"
    )


@app.route("/matrix", methods=["GET"])
def matrix():

    return render_template("matrix.html", page_title="Allocation Matrix", authors=authors_shuffle())


@app.route("/payments", methods=["GET"])
def payments():

    return render_template("payments.html", page_title="Payments", authors=authors_shuffle())


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact_us.html", page_title="Contact Us", authors=authors_shuffle())


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


@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.id[2:] == 'EB':
        return render_template("eb-dashboard.html", name=current_user.name)
    return render_template("dashboard.html", name=current_user.name)


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
    return redirect(url_for('dashboard'))


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


@app.route('/update-db')
def update_eb():
    quickstart()
    print('---------------\nLoaded data from sheet\n---------------')
    generate_sheet()

    return send_file(ROOT_DIR + '/static/Users.xlsx')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, threaded=True)
