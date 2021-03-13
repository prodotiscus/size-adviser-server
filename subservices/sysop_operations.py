#!/usr/bin/python3

from datetime import datetime

from db_admins import AdminDatabase
from db_computations import brand_of_file
from db_computations import db_load_sheets

from collections import namedtuple

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory

from typing import Iterator, Dict, List

import os
import random
from shutil import copyfile


sysop = Blueprint("sysop", __name__, static_folder="static", template_folder="templates")


@sysop.route("/signin")
def admin_signin():
    return send_from_directory("static", "login.html")


@sysop.route("/signin-submission", methods=["POST"])
def admin_signin_submission():
    username = request.form["username"]
    pwd = request.form["password"]
    adb = AdminDatabase()
    token = adb.get_token(username, pwd)
    adb.exit()
    resp = make_response(redirect("/sysop/p" if token != "notoken" else "/sysop/signin"))
    resp.set_cookie("adminun", username)
    resp.set_cookie("admintkn", token)
    return resp


@sysop.route("/_unf")
def upload_as__shortcut():
    if "sheet-code" not in request.args:
        return redirect("/sysop/sheets")
    return redirect("/sysop/upload_as/%s.xlsx" % str(request.args["sheet-code"]))


@sysop.route("/upload_as/<name_of_file>")
def upload_as(name_of_file):
    return render_template("upload_as.html", name_of_file=name_of_file)


@sysop.route("/update_file/<fname>", methods=["GET", "POST"])
def update_file(fname):
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get("adminun"), request.cookies.get("admintkn"))
    adb.exit()
    if not istrue:
        return redirect("/sysop/signin")

    if request.method == "POST":
        if "file" not in request.files:
            return redirect("/sysop/p")
        file = request.files["file"]
        if file.filename == "":
            return redirect("/sysop/p")
        if file:
            file.save(os.path.join(os.path.split(sysop.root_path)[0], "sheets/brands", fname))
            db_load_sheets(dirname=os.path.join(os.path.split(sysop.root_path)[0], "sheets/brands"))
            return redirect("/sysop/sheets")

    return redirect("/error/Unknown error, try again/upload_as/" + fname)


sheet_item = namedtuple("sheet_item", "filename last_modified brand internal_code")


def iterate_sheets() -> Iterator[sheet_item]:
    path = os.path.abspath(".")
    files = os.listdir(os.path.join(path, "sheets", "brands"))
    files = ["CATALOGUE.xlsx"] + [f for f in files if "CATALOGUE" not in f]
    for e, filename in enumerate(files):
        try:
            mtime = os.path.getmtime(os.path.join(path, "sheets", "brands", filename))
        except OSError:
            mtime = 0
        last_modified = datetime.fromtimestamp(mtime)
        bof = brand_of_file(filename) if e > 0 else ""
        index = filename.split(".")[0] if e > 0 else ""
        yield sheet_item(
            filename=filename,
            last_modified=last_modified,
            brand=bof,
            internal_code=index
        )


@sysop.route("/wo-table.json")
def wo_table_json():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get("adminun"), request.cookies.get("admintkn"))
    adb.exit()
    if not istrue:
        return redirect("/sysop/signin")



@sysop.route("/p")
@sysop.route("/list-files")
@sysop.route("/sheets")
def list_sheets():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get("adminun"), request.cookies.get("admintkn"))
    adb.exit()
    if not istrue:
        return redirect("/sysop/signin")
    path = os.path.abspath(".")
    files = os.listdir(os.path.join(path, "sheets", "brands"))
    files = ["CATALOGUE.xlsx"] + [f for f in files if "CATALOGUE" not in f]
    file_rows: List[sheet_item] = [s for s in iterate_sheets()]

    return render_template("files.html", file_rows=file_rows)


@sysop.route("/load_sheet", methods=["GET", "POST"])
@sysop.route("/sheet_acquire/<tname>")
def load_sheet(tname=None):
    if tname is None and "sheet-code" in request.form:
        tname = request.form["sheet-code"] + ".xlsx"

    elif tname is None:
        return redirect("/sysop/sheets")

    if ":" not in tname:
        num = random.randrange(100000, 999999)
        copyname = "%s:%d.XLSX" % (tname, num)
        try:
            copyfile(os.path.join("sheets", "brands", tname), os.path.join("copied", copyname))
        except FileNotFoundError:
            return redirect("/error/%s/%s" % ("No file holding the given number found", "sheets"))
        return redirect("/sysop/sheet_acquire/" + copyname)

    else:
        return send_from_directory("copied", tname)


@sysop.route("/git-pull-webhook", methods=["GET", "POST"])
def git_pull_on_webhook():
    #cwd = os.getcwd()
    #os.chdir("")
    return sysop.root_path
