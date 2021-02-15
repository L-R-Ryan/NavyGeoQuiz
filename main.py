import os

from flask import Flask, flash, jsonify, redirect, render_template, request
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import random

import mysql.connector
from mysql.connector.constants import ClientFlag

config = {
    'user': 'root',
    'password': 'navyquiz8',
    'host': '35.199.59.94',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'server-ca.pem',
    'ssl_cert': 'client-cert.pem',
    'ssl_key': 'client-key.pem'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


##drop all tables
#tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#tables.pop(0)
#for t in tables:
#    table = t['name']
#    cursor.execute("drop table if exists :table",table=table)

# Initialize a number for a unique database
user_id = 0
user_slide = ''
user_slides = ''
str_user_id = ''


@app.route("/", methods=["GET", "POST"])
def start():
    # initalize all global variables
    global user_id
    global user_slide
    global user_slides
    global str_user_id
    if request.method == "POST":

        #create a table of slides unique to a user. Insert the slides the user selected into the table.
        user_slides = "slides"+str(user_id)
        cursor.execute("create table :slides (slide VARCHAR(50))", slides=user_slides)
        conn.commit()
        for value in request.form:
            if value != 'selectall':
                cursor.execute("insert into :slides (slide) VALUES (:value)", slides=user_slides, value=value+str(user_id))
                conn.commit()

        return redirect("quiz")
    else:

        #create a unique id for each user
        user_id = random.randint(1,10000)
        #tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name LIKE :user_id", user_id=user_id)
        #tables.pop(0)
        #for t in tables:
        #    table = t['name']
        #    cursor.execute("drop table if exists :table",table=table)

        return render_template("start.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    answers = {}
    method = request.method

    #get slides that the user selected and put them in a list
    slides = []
    print(user_id)
    str_user_id ='%' + str(user_id)
    get_slides = cursor.execute("select * from :slides where slide like :user", slides=user_slides, user=str_user_id)

    for slide in get_slides:
        slides.append(slide['slide'])

    #get tables already created. This is currently broken because we need to access tables unique to user id.
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name like '%.html%' and name like :user", user=str_user_id)

    print(tables)
    print(slides)

    #remove table from slides if it already exists
    for t in tables:
        table = t['name']
        table=table
        slides.remove(table)

    #direct to final score if <<something>> otherwise render the next template in the list.
    if request.form.get("template") is None:
        if len(slides) > 0:
            slides[0] = slides[0].split('.html',1)[0]
            return render_template(slides[0]+".html")
        return redirect("final_score")

    #gets slide id. add user id here?
    slide_id = (request.form.get("template"))
    user_slide = slide_id+str(user_id)

    #gets user answers
    for key in request.form:
        answers[key] = (request.form.get(key))

    del answers["template"]
    cursor.execute("drop table if exists :table",table=user_slide)
    conn.commit()
    cursor.execute("create table :table (correct VARCHAR(50), user_input VARCHAR(50), is_correct VARCHAR(20), color VARCHAR(20))", table=user_slide)
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
        cursor.execute("insert into :table (correct, user_input, is_correct, color) VALUES (:correct, :user_input, :is_correct, :color)",
        table=user_slide, correct=a, user_input=answers[a], is_correct=is_correct, color=color)
        conn.commit()

    print(slide_id)
    img_id = slide_id
    img_id = img_id.replace("html", "jpg")
    print(img_id)
    answers_to_score = cursor.execute("select * from :table", table=user_slide)

    return render_template("score.html", slide_id=user_slide, answers_to_score=answers_to_score, img_id=img_id)

@app.route("/final_score", methods=["GET", "POST"])
def final_score():
    str_user_id ='%' + str(user_id)
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name like '%.html%' and name like :user", user=str_user_id)

    total = 0
    correct = 0

    for t in tables:
        table = t['name']
        ans = cursor.execute("select * from :table", table=table)
        total += len(ans)
        #print(ans)
        for a in ans:
            if (a['correct']).lower() == (a['user_input']).lower():
                correct += 1

    if total * correct == 0:
        score = 0
    else:
        score = round(100/total * correct)

    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name like :user", user=str_user_id)
    tables.pop(0)
    for t in tables:
            table = t['name']
            cursor.execute("drop table if exists :table",table=table)
            conn.commit()
    conn.close()
    return render_template("final_score.html", score=score)
