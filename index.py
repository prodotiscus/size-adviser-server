#!/usr/bin/python3

from datetime import datetime

from db_admins import AdminDatabase
from db_computations import brand_of_file
from db_computations import ComputationsDbSession
from db_computations import db_load_sheets
from db_computations import sheet_records
from db_personal import FittingSession
from db_personal import save_user_props

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory

from subserv_mobile import mobile

from shutil import copyfile
from werkzeug.utils import secure_filename

import os
import random

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "files")
app.config["ALLOWED_EXTENSIONS"] = {".xlsx", ".xls", ".jpg", ".jpeg", ".png"}


@app.route("/admin-signin")
def admin_signin():
    return send_from_directory("static", "login.html")


@app.route("/admin-signin-submission", methods=["POST"])
def admin_signin_submission():
    username = request.form["username"]
    pwd = request.form["password"]
    adb = AdminDatabase()
    token = adb.get_token(username, pwd)
    adb.exit()
    resp = make_response(redirect("/p" if token != "notoken" else "/admin-signin"))
    resp.set_cookie('adminun', username)
    resp.set_cookie('admintkn', token)
    return resp


@app.route("/_unf")
def upload_as__shortcut():
    if "sheet-code" not in request.args:
        return redirect("/sheets")
    return redirect("/upload_as/%s.xlsx" % str(request.args["sheet-code"]))


@app.route("/upload_as/<name_of_file>")
def upload_as(name_of_file):
    return render_template("upload_as.html", name_of_file=name_of_file)


@app.route("/update_file/<fname>", methods=["GET", "POST"])
def update_file(fname):
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get("adminun"), request.cookies.get("admintkn"))
    adb.exit()
    if not istrue:
        return redirect("/admin-signin")

    if request.method == "POST":
        if "file" not in request.files:
            return redirect("/p")
        file = request.files["file"]
        if file.filename == "":
            return redirect("/p")
        if file:
            file.save(os.path.join(app.root_path, "sheets/brands", fname))
            db_load_sheets(dirname=os.path.join(app.root_path, "sheets/brands"))
            return redirect("/sheets")

    return redirect("/error/Unknown error, try again/upload_as/" + fname)


@app.route("/p")
@app.route("/list-files")
@app.route("/sheets")
def list_sheets():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get("adminun"), request.cookies.get("admintkn"))
    adb.exit()
    if not istrue:
        return redirect("/admin-signin")
    path = os.path.abspath(".")
    files = os.listdir(os.path.join(path, "sheets", "brands"))
    files = ["CATALOGUE.xlsx"] + [f for f in files if "CATALOGUE" not in f]
    file_rows = []
    for e, filename in enumerate(files):
        try:
            mtime = os.path.getmtime(os.path.join(path, "sheets", "brands", filename))
        except OSError:
            mtime = 0
        last_modified = datetime.fromtimestamp(mtime)
        bof = brand_of_file(filename) if e > 0 else ""
        index = filename.split(".")[0] if e > 0 else ""
        file_rows.append(dict(
            filename=filename,
            last_modified=last_modified,
            brand=bof,
            internal_code=index
        ))

    return render_template("files.html", file_rows=file_rows)


@app.route("/load_sheet", methods=["GET", "POST"])
@app.route("/sheet_acquire/<tname>")
def load_sheet(tname=None):
    if tname is None and "sheet-code" in request.form:
        tname = request.form["sheet-code"] + ".xlsx"

    elif tname is None:
        return redirect("/sheets")

    if ":" not in tname:
        num = random.randrange(111111, 999999)
        copyname = "%s:%d.XLSX" % (tname, num)
        try:
            copyfile(os.path.join("sheets", "brands", tname), os.path.join("copied", copyname))
        except FileNotFoundError:
            return redirect("/error/%s/%s" % ("No file holding the given number found", "sheets"))
        return redirect("/sheet_acquire/" + copyname)

    else:
        return send_from_directory("copied", tname)


'''


@app.route("/upload-bm-file", methods=["GET", "POST"])
def upload_bm_files():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({
                "error": "no_file_specified"
            })

        if "brand" not in request.form or "model" not in request.form:
            return jsonify({
                "error": "no_brand_model_data"
            })
        else:
            brand, model = request.form["brand"], request.form["model"]

        if "size" in request.form:
            size = request.form["size"]
        else:
            size = None

        if "userid" in request.form:
            user = request.form["user"]
        else:
            user = None

        file = request.files["file"]
        if file.filename == "":
            return jsonify({
                "error": "filename_not_found"
            })

        if file:
            extension = file.filename.split(".")[-1]
            fname = photos.new_photo_id(brand, model, extension)
            file.save(os.path.join(app.root_path, "files", fname))
            photos.add_photo(brand, model, size, fname, user)
            return jsonify({
                "new_photo_id": fname
            })
'''


app.register_blueprint(mobile, url_prefix="/mobile")


@app.route("/error/<text>/<path:returnto>")
def throw_error(text, returnto):
    return render_template("error.html", text=text, returnto=returnto)


@app.route('/st/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route("/")
def welcome():
    return redirect("/error/Authorization needed/p")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
