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


@firebase.route("/register_new_account")
def register_new():
    """Used in SizeAdviserApi"""
    firebase_uid = request.args.get("firebase_uid")
    user_email = request.args.get("user_email")
    user_name = request.args.get("user_name")
    user_gender = int(request.args.get("user_gender"))
    rewrite = request.args.get("rewrite") is not None

    if firebase_uid is None or user_email is None or user_name is None or user_gender is None:
        return abort(400)

    db = sqlite3.connect("../DATABASES/personal.sqlite3")
    c = db.cursor()
    exists = c.execute(f"SELECT firebase_uid FROM firebase_accounts WHERE firebase_uid='{firebase_uid}'").fetchone()
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
            f"WHERE firebase_uid='{firebase_uid}'",
            (user_email, user_name, user_gender, dumps({}))
        )
    db.commit()
    db.close()

    return jsonify({
        "status": "success",
        "code": "registered" if not rewrite else "updated"
    })
