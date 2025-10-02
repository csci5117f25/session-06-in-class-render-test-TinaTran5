from flask import Flask, render_template, request, session
import db
import os

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET']
db.setup()


@app.route("/")
@app.route("/<name>")
def hello(name=None):
    if name is not None: 
        session["name"] = name
    return render_template(
        "hello.html", name=session.get("name"), guestbook=db.get_guestbook()
    )



@app.post("/submit")
def submit():
    name = request.form.get("name")
    text = request.form.get("text")
    db.add_post(name, text)
    return render_template("hello.html", name=None, guestbook=db.get_guestbook())