from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)
DATABASE = "maori-dictionary.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


def is_logged_in():
    if session.get("email") is None:
        print('Not logged in')
        return False
    print('Logged In')
    return True


def get_categories():
    con = create_connection(DATABASE)
    print(con)
    query = "SELECT id, name FROM categories ORDER BY name ASC"
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return category_list


@app.route('/category/<cat_id>')
def render_dict(cat_id):
    con = create_connection(DATABASE)
    query = "SELECT id, maori_word, english_word, image FROM dictionary WHERE cat_id=? ORDER BY maori_word ASC"
    cur = con.cursor()
    cur.execute(query, (cat_id))
    word_list = cur.fetchall()
    con.close
    return render_template("home.html", logged_in=is_logged_in(), categories=get_categories(), words=word_list)


@app.route('/login')
def render_login():
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        con = create_connection(DATABASE)
        query = 'SELECT id, fname, FROM users WHERE email =? AND password =?'
        cur = con.cursor()
        cur.execute(query, (email, password))
        user_data = cur.fetchall()
        con.close()

        if user_data:
            user_id = user_data[0][0]
            fname = user_data[0][1]
            print(user_id, fname)

            session['email'] = email
            session['user_id'] = user_id
            session['fname'] = fname

            return redirect("/menu")

        else:
            return redirect()
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        con = create_connection(DATABASE)

        query = "INSERT INTO user (fname, lname, email, password) VALUES (?,?,?,?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            return redirect("/signup?error=Email+already+in+use")
        con.commit()
        con.close()
        return redirect('/login')

    return render_template('signup.html')


@app.route('/')
def render_home():
    return render_template("home.html", categories=get_categories(), logged_in=is_logged_in())


if __name__ == '__main__':
    app.run()