#flask_session may not be included when generating requirements.txt If manually
#add this flask-session=0.3.1 and Werkzeug==0.16.0

import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import random

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

import mysql.connector
from mysql.connector.constants import ClientFlag

config = {
    'user': 'root',
    'password': 'navyquiz8',
    'host': '35.199.59.94',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'server-ca.pem',
    'ssl_cert': 'client-cert.pem',
    'ssl_key': 'client-key.pem',
    'database': 'navyquizdb'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor(buffered=True, dictionary=True)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Initialize a number for a unique database
#session['user_id'] = 0
#session['user_slide'] = ''
#session['user_slides'] = ''
#session['str_user_id'] = ''


@app.route("/", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        #create a table of slides unique to a user. Insert the slides the user selected into the table.
        user_id = session.get('user_id')
        session['user_slides'] = "slides"+str(user_id)
        cursor.execute("create table "+session['user_slides']+" (slide VARCHAR(50))")
        conn.commit()
        for value in request.form:
            if value != 'selectall':
                cursor.execute("insert into "+session['user_slides']+" (slide) VALUES ('"+str(user_id)+value+"')")
                conn.commit()

        return redirect("quiz")
    else:

        #create a unique id for each user
        session['user_id'] = random.randint(1000,9999)

        return render_template("start.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    #get session variables
    user_id = session.get('user_id')
    user_slides = session.get('user_slides')

    answers = {}
    method = request.method

    #get slides that the user selected and put them in a list
    slides = []
    str_user_id = str(user_id) +'%'
    print (str_user_id)
    query = ("select * from "+user_slides+" where slide like '"+str_user_id+"'")
    print(query)
    cursor.execute("select * from "+user_slides+" where slide like '"+str_user_id+"'")
    get_slides = cursor.fetchall()

    for slide in get_slides:
        slides.append(slide['slide'])

    #get tables already created.
    cursor.execute("SELECT table_name from information_schema.tables where table_name not like 'slides%' and table_name like '"+str_user_id+"'")
    tables = cursor.fetchall()

    print(slides)
    print(tables)
    #remove table from slides if it already exists
    for t in tables:
        table = t['table_name'] + '.html'
        print ("table is")
        print (table)
        slides.remove(table)

    #direct to final score if <<something>> otherwise render the next template in the list.
    if request.form.get("template") is None:
        if len(slides) > 0:
            slides[0] = slides[0].split(str(user_id),1)[1]
            return render_template(slides[0])
        return redirect("final_score")

    #gets slide id, remove .html to make sql friendly, add session['user_id']
    slide_id = (request.form.get("template"))
    sql_slide_id = slide_id.split('.',1)[0]
    session['user_slide'] = str(user_id) + sql_slide_id

    #gets user answers
    for key in request.form:
        answers[key] = (request.form.get(key))

    del answers["template"]
    cursor.execute("drop table if exists "+session['user_slide'])
    conn.commit()
    cursor.execute("create table "+session['user_slide']+" (correct VARCHAR(50), user_input VARCHAR(50), is_correct VARCHAR(20), color VARCHAR(20))")
    conn.commit()

    color = ''

    #adds answers to table, including whether the user answer was correct or incorrect.
    for a in answers:
        if a.lower() == answers[a].lower():
            is_correct = 'Correct!'
            color = ''
        else:
            is_correct = 'Incorrect!'
            color = '#800000'
        cursor.execute("insert into "+session['user_slide']+" (correct, user_input, is_correct, color) VALUES ('"+a+"', '"+answers[a]+"', '"+is_correct+"', '"+color+"')")
        conn.commit()

    img_id = slide_id
    img_id = img_id.replace("html", "jpg")
    cursor.execute("select * from "+session['user_slide'])
    answers_to_score = cursor.fetchall()

    return render_template("score.html", slide_id=session['user_slide'], answers_to_score=answers_to_score, img_id=img_id)

@app.route("/final_score", methods=["GET", "POST"])
def final_score():
    str_user_id = session.get('str_user_id')
    cursor.execute("SELECT table_name from information_schema.tables where table_name not like 'slides%' and table_name like '"+str_user_id+"'")
    tables = cursor.fetchall()

    total = 0
    correct = 0

    for t in tables:
        table = t['table_name']
        cursor.execute("select * from "+table)
        ans = cursor.fetchall()
        total += len(ans)
        #print(ans)
        for a in ans:
            if (a['correct']).lower() == (a['user_input']).lower():
                correct += 1

    if total * correct == 0:
        score = 0
    else:
        score = round(100/total * correct)

    cursor.execute("SELECT table_name from information_schema.tables where table_name like '"+str_user_id+"' ")
    tables = cursor.fetchall()
    print("final score tables are")
    print(tables)
    for t in tables:
            table = t['table_name']
            cursor.execute("drop table if exists "+table)
            conn.commit()
    conn.close()
    session.clear()
    return render_template("final_score.html", score=score)
