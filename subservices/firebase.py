#!/usr/bin/python3

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import render_template

import sqlite3

firebase = Blueprint("firebase", __name__, template_folder="templates")


@firebase.route("/facebook_auth")
def facebook_auth():
    return render_template("firebase_auth.html")


@firebase.route("/google_auth")
def google_auth():
    return render_template("google_auth.html")


@firebase.route("/set_session_data")
def set_session_data():
    session_id = request.args.get("session_id")
    user_email = request.args.get("user_email")
    user_name = request.args.get("user_name")
    if not session_id or not user_email or not user_name:
        return abort(400)
    v = [session_id, user_email, user_name]
    db = sqlite3.connect("databases/personal.sqlite3")
    c = db.cursor()
    c.execute("INSERT INTO firebase_sessions VALUES (?, ?, ?)", v)
    db.commit()
    db.close()
    return jsonify({
        "status": "success",
        "message": "Session data successfully recorded to the database."
    })


@firebase.route("/get_session_data")
def get_session_data():
    session_id = request.args.get("session_id")
    preserve_row = request.args.get("preserve", False)
    if not session_id:
        return abort(400)

    db = sqlite3.connect("databases/personal.sqlite3")
    c = db.cursor()
    d = c.execute("SELECT user_email, user_name FROM firebase_sessions WHERE session_id='%s'" % session_id).fetchone()
    try:
        d = d[0]
    except IndexError:
        return abort(400)
    if d is None:
        return abort(400)

    if not preserve_row:
        c.execute("DELETE FROM firebase_sessions WHERE session_id='%s'" % session_id)
    db.commit()
    db.close()

    return jsonify({
        "status": "success",
        "data": {
            "email": d[0],
            "name": d[1]
        }
    })
