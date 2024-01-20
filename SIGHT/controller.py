from flask import Flask, url_for, request, redirect, session, jsonify
from flask import render_template, session
from flask import current_app as app
from flask_cors import CORS, cross_origin
from backend.locator import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, support_credentials=True)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route("/validation")
def validation():
    
	    return render_template('validation.html')


@app.route("/map")
def map():
    return render_template('map.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        cur.execute('SELECT * FROM Users;')
        users = cur.fetchall()
        # print(users)
        
        for i in users:
            if i[1] == email and i[3] == str(password):
                print('found user')
                session['uid']=i[0]
                return redirect(url_for('dashboard'))

        return render_template('login.html', msg='Wrong credentials,try again')
    return render_template('login.html', msg='')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            print('inside signup',username)
            cur.execute('SELECT * FROM Users;')
            users = cur.fetchall()
            print(users)
            for i in users:
                if i[1] == email:
                    print('user exist already')
                    return "User exist already"
            cur.execute("INSERT INTO Users (email, name, password) VALUES (%s, %s, %s)",
                        (email, username, password))
            conn.commit()
            print('user added')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            
    return render_template('signup.html')


@app.route('/rank', methods=['POST', 'GET'])
def rank():
    if request.method == 'POST':
        print('rank called')

        data = request.form.get('cords')

        data = [float(i) for i in data.split(',')]
        cords = [(data[i], data[i+1]) for i in range(0, len(data), 2)]

        type_ = request.form.get('type')
        size = request.form.get('size')
        result = get_rank(cords, type_, size)
        print(result)
        return jsonify(result)
    return 'Provide query'


@app.route('/validator', methods=['POST', 'GET'])
def valid():
    if request.method == 'POST':
        print('validator called')

        type_ = request.form.get('industry')
        uid = session.get('uid', 0)
        description = request.form.get('description')
        valid = validator(uid, type_, description)

        return jsonify({'discription': valid})
    return 'Provide query'


if __name__ == '__main__':
    app.run(debug=True)
