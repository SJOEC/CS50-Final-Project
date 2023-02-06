from flask import Flask, flash, redirect, render_template, request, session

from flask_session import Session
from helpers import login_required, apology, have_number

from werkzeug.security import check_password_hash, generate_password_hash

from cs50 import SQL

from datetime import datetime

app = Flask(__name__)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///leveling.db")

# Custome iteration
app.jinja_env.filters['zip'] = zip

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#create variable to use alerts
context={
    "type": "",
    "message": ""
}


@app.route('/', methods=["GET", "POST"])
@login_required
def index():  # put application's code here

    if request.method == "POST":

        # Add task to the db
        tmp_task = request.form.get("task")

        db.execute("INSERT INTO tasks (?,?) VALUES (?,?)", "user_id", "task", session["user_id"], tmp_task)

        # get total tasks number
        tmp_tasks_number = db.execute("SELECT tasks_number FROM users WHERE id = ?", session['user_id'])

        tmp_tasks_number = int(tmp_tasks_number[0]['tasks_number'])

        total_tasks = tmp_tasks_number + 1

        #update in db
        db.execute("UPDATE users SET ? = ? WHERE id = ?", "tasks_number", total_tasks, session['user_id'] )

        last_task = db.execute("SELECT task_id,task FROM tasks WHERE user_id = ? ORDER BY task_id DESC LIMIT 1", session['user_id'])
        last_task = last_task[0]

        #update history
        db.execute("INSERT INTO history (?,?,?,?) VALUES (?,?,?,?)", "record_task_id", "task_text", "record_user_id", "time", last_task['task_id'], last_task['task'], session['user_id'], datetime.now())

        return redirect("/")

    else:

        username = db.execute("SELECT username FROM users WHERE id = ?", session['user_id'])
        username = username[0]['username']

        actual_tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", session["user_id"])

        n = []

        for i in range(len(actual_tasks)):
            n.append(i)

        return render_template("index.html", foo=actual_tasks, bar=n, zip=zip, username=username)


"""
@app.route('/update_points/<string:user_points>', methods=['POST'])
def update_points(user_points):

    user_points = json.load(user_points)

    print('SUCESS')
    print(f"user points {user_points['points']}")

    return 'OK'
"""


@app.route('/remove', methods=["POST"])
def remove():
    if request.method == "POST":

        tmp = request.form.get("mycheckbox")

        db.execute("DELETE FROM tasks WHERE task = ? AND user_id = ?", tmp, session['user_id'])

        return redirect("/")

@app.route('/login', methods=["GET", "POST"])
def login():


    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("login_username"):
            return apology("must provide username ", 403)

        # Ensure password was submitted
        elif not request.form.get("login_password"):
            return apology("must provide password ", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("login_username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("login_password")):
            return apology("must provide password ", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    if request.method == "GET":

        return render_template("login.html")


@app.route('/register', methods=["POST"])
def register():

        if request.method == "POST":  # if the user submit the forum, create the user

            symbols = [";", ".", ",", "+", "*", "&", "!", ":", "-", "?", "¡", "|"]
            usersnames = []
            password_check = False

            # locate the users in a tmp variable
            users = db.execute("SELECT username FROM users")
            if len(users) > 0:
                users = users[0]['username']

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)

            # check if username is already taken

            users = db.execute("SELECT username FROM users")

            for i in range(len(users)):
                usersnames.append(users[i]['username'])

            if request.form.get("username") in usersnames:
                return apology("Username already taken", 400)

            # Ensure password was submitted
            if not request.form.get("password"):
                return apology("must provide password", 400)

            if not request.form.get("confirmation"):
                return apology("must confirm password", 400)

            # check password requirements
            if len(request.form.get("password")) < 4:
                return apology("password does not have enough characters", 400)

            for i in range(len(symbols)):
                if symbols[i] in request.form.get("password"):
                    password_check = True
                    break

            if have_number(request.form.get("password")) == False:
                return apology("password need a number", 400)

            # check both passwords
            if request.form.get("password") != request.form.get("confirmation"):
                return apology("password do not match", 400)

            if password_check == False:
                return apology("password need special character", 400)

            # register user
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", request.form.get(
                "username"), generate_password_hash(request.form.get("password")))

            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]


            return redirect("/")

@app.route('/profile', methods=["GET"])
@login_required
def profile():

    # gets user's username
    username = db.execute("SELECT username FROM users WHERE id = ?", session['user_id'])
    username = username[0]['username']

    # get total tasks number
    tmp_tasks_number = db.execute("SELECT tasks_number FROM users WHERE id = ?", session['user_id'])

    tmp_tasks_number = int(tmp_tasks_number[0]['tasks_number'])

    # gets tasks data
    last_task = db.execute("SELECT record_task_id,task_text,time FROM history WHERE record_user_id = ? ORDER BY record_task_id DESC LIMIT 8", session['user_id'])

    return render_template("profile.html", username=username, total_tasks=tmp_tasks_number, foo=last_task,zip=zip)




@app.route('/logout')

def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

    