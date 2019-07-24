from flask import Flask, render_template, request, redirect, session ,flash
from db import connectToMySQL
import re
from flask_bcrypt import Bcrypt 




app = Flask(__name__)
app.secret_key = 'dojo'
bcrypt = Bcrypt(app)
db = connectToMySQL('shaped')



@app.route('/')
def root():
    db = connectToMySQL('shaped')
    return render_template('login.html')

	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
alpha = re.compile(r'^[a-zA-Z]$')

@app.route('/add', methods=['POST'])
def show():
    db = connectToMySQL("shaped")
    query = 'SELECT COUNT(email) FROM users WHERE email LIKE %(email)s'
    data = {
        'email' : request.form['email']
    }
    email = db.query_db(query,data)
    
    if len(request.form['first_name']) < 2:
        flash("Please enter your first name", 'fname')
    else:
        session['first_name'] = request.form['first_name']
    if len(request.form['last_name']) < 2:
        flash("Please enter your last name", 'lname')
    else:
        session['last_name'] = request.form['last_name']
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!", 'email')
    else:
        session['email'] = request.form['email']
    if len(request.form['password']) < 8:
        flash('Password must be over 8 characters','pw')
        session['password'] = request.form['password']
        return redirect('/')
    if (request.form['password_confirm']) != request.form['password']:
        flash("Please confirm password",'pw_con')    
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password']) 
    session['pw_hash'] = pw_hash 
    print(pw_hash)
    db = connectToMySQL("shaped")
    query2 = "INSERT INTO users (first_name, last_name ,email,pw_hash, created_at, updated_at) VALUES (%(fn)s, %(ln)s,%(email)s,%(pw_hash)s, NOW(), NOW())"
    data2 ={
            'fn' : request.form['first_name'],
            'ln' : request.form['last_name'],
            'email' : request.form['email'],
            'pw_hash' : pw_hash
    }
    print (query)
    id = db.query_db(query2,data2)
    session['userid'] = id
    return redirect('/showUsers')

@app.route('/login', methods=['POST'])
def login():
    if len(request.form['email']) == 0:
        flash('please enter email')
    db = connectToMySQL("shaped")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {'email' : request.form['email']}
    user = db.query_db(query,data)
    if user:
        if request.form['email'] == user[0]['email']:
            session['name'] = user[0]['first_name']
        if bcrypt.check_password_hash(user[0]['pw_hash'], request.form['password']):
            session['name'] = user[0]['first_name']
            session['userid'] = user[0]['id']
            flash("You could not be logged in",'pw')
            return redirect('/showUsers')
            
    return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/goals", methods=['POST'])
def setGoals():
    db = connectToMySQL("shaped")
    query = "INSERT INTO goal (goal, created_at, updated_at, users_id) VALUES (%(go)s, NOW(), NOW(), %(users_id)s)"
    data = {
        'go' : request.form['goal'],
        'users_id' : session['userid']
    }
    user = db.query_db(query, data)

    return redirect("/showUsers")

@app.route('/showUsers')
def create_user():
    if 'userid' not in session:
        return redirect('/')

    db = connectToMySQL("shaped")
    query = "SELECT * FROM users"
    user = db.query_db(query)    
    print(user)
    session['user'] = user
    session['first_name'] = user

    db = connectToMySQL('shaped')
    query1 = "SELECT goal, goal.created_at, users_id, users.first_name,goal.id FROM goal JOIN users ON users.id = goal.users_id WHERE users.id= "+ str(session['userid'])
    print(query)
    goal = db.query_db(query1)
    print(goal)
    session['goal'] = goal

    db = connectToMySQL('shaped')
    query1 = "SELECT tips, description, users_id, users.first_name ,tips.id FROM tips JOIN users ON users.id = tips.users_id "
    tips = db.query_db(query1)
    session['tip'] = tips

    return render_template('index.html',user = user, id= session['userid'], goal=goal, tips = tips)

@app.route('/show/<id>') 
def showTip(id):
    db = connectToMySQL('shaped')
    query1 = "SELECT tips, description, users_id, users.first_name ,tips.id FROM tips JOIN users ON users.id = tips.users_id WHERE tips.id = " +str(id)
    tips = db.query_db(query1)
    print(tips)

    return render_template("show.html", x=tips)

@app.route('/delete/<id>')
def delete(id):
    print(id)
    db = connectToMySQL("shaped")
    query = "DELETE FROM goal WHERE id="+ str(id)
    db.query_db(query)
    
    db = connectToMySQL("shaped")
    query1 = "DELETE FROM messages WHERE id="+str(id)
    db.query_db(query1)

    return redirect('/showUsers')

@app.route('/delete1/<id>')
def delete1(id):
    print(id)
    
    db = connectToMySQL("shaped")
    query1 = "DELETE FROM messages WHERE id="+str(id)
    db.query_db(query1)

    return redirect('/chat')
    
@app.route('/findGym')
def findGym():
    if 'userid' not in session:
        return redirect('/')
        

    return render_template("find.html")

@app.route("/chat")
def chat():
    if 'userid' not in session:
        return redirect('/')

    db = connectToMySQL("shaped")
    query = "SELECT * FROM users"
    user = db.query_db(query)    
    print(user)
    session['user'] = user
    session['first_name'] = user

    db = connectToMySQL('shaped')
    query1 = "SELECT message, recipient_id, users_id, users.first_name ,messages.id FROM messages JOIN users ON users.id = messages.users_id WHERE recipient_id = "+ str(session['userid'])
    message = db.query_db(query1)
    print(message)
    session['message'] = message

    return render_template("chat.html", user = user, message = message)
    
@app.route('/send', methods=['POST'])
def message():
    print(request.form['recipient_id'])
    db = connectToMySQL("shaped")
    print("Session name ********", session['name'])
    query1 = 'INSERT INTO messages (message, recipient_id, created_at, updated_at, users_id) VALUES (%(msg)s, %(recepient)s, NOW(), NOW(), %(users_id)s)'
    data = {
        'msg' :request.form['message'],
        'recepient' :request.form['recipient_id'],
        'users_id' : session['userid']
    }
    user = db.query_db(query1, data)

    
    return redirect('/chat')

@app.route("/newTips", methods = ['POST'])
def newTips():
    db = connectToMySQL("shaped")
    query1 = 'INSERT INTO tips (tips, description, created_at, updated_at, users_id) VALUES (%(tip)s, %(desc)s, NOW(), NOW(), %(users_id)s)'
    data = {
        'tip' :request.form['tips'],
        'desc' :request.form['description'],
        'users_id' : session['userid']
    }
    user = db.query_db(query1, data)

    return redirect("/showUsers")

@app.route("/newTip")
def tip():
    return render_template("tip.html")


if __name__ == "__main__":
    app.run(debug=True)