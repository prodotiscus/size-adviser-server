#!/usr/bin/python3

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import render_template

from json import dumps, loads
from random import randint
import sqlite3

firebase = Blueprint("firebase", __name__, template_folder="templates")


@firebase.route("/facebook_auth/<session_id>")
def facebook_auth(session_id):
    return render_template("facebook_auth.html", session_id=session_id)


@firebase.route("/google_auth/<session_id>")
def google_auth(session_id):
    return render_template("google_auth.html", session_id=session_id)


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


@firebase.route("/generate_session_id")
def generate_session_id():
    return jsonify({
        "new_id": str(randint(10**(8-1), (10**8)-1))
    })


@firebase.route("/register_new_account")
def register_new():
    firebase_uid = request.args.get("firebase_uid")
    user_email = request.args.get("user_email")
    user_name = request.args.get("user_name")
    user_gender = int(request.args.get("user_gender"))
    rewrite = request.args.get("rewrite") is not None

    if firebase_uid is None or user_email is None or user_name is None or user_gender is None:
        return abort(400)

    db = sqlite3.connect("databases/personal.sqlite3")
    c = db.cursor()
    exists = c.execute("SELECT firebase_uid FROM firebase_accounts WHERE firebase_uid='%s'" % firebase_uid).fetchone()
    if exists and not rewrite:
        db.close()
        return jsonify({
            "status": "success",
            "code": "already_exists"
        })

    if not rewrite:
        c.execute(
            "INSERT INTO firebase_accounts VALUES (?, ?, ?, ?, ?)",
            (firebase_uid, user_email, user_name, user_gender, dumps({}))
        )
    else:
        c.execute(
            "UPDATE firebase_accounts SET user_email=?, user_name=?, user_gender=?, additional=? "
            "WHERE firebase_uid='%s'" % firebase_uid,
            (user_email, user_name, user_gender, dumps({}))
        )
    db.commit()
    db.close()

    return jsonify({
        "status": "success",
        "code": "registered" if not rewrite else "updated"
    })
