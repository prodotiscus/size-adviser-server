#!/usr/bin/python3

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
from logging.handlers import WatchedFileHandler
from shutil import copyfile

import os
import random

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "files")
app.config["ALLOWED_EXTENSIONS"] = {".xlsx", ".xls", ".jpg", ".jpeg", ".png"}


@app.before_first_request
def setup_logging():
    handler = WatchedFileHandler("/var/log/size-adviser.log")
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


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


@app.route("/sheets")
def list_sheets():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get('adminun'), request.cookies.get('admintkn'))
    adb.exit()
    if not istrue:
        return redirect("/admin-signin")
    path = os.path.abspath(".")
    files = os.listdir(os.path.join(path, "sheets", "brands"))
    files = ["CATALOGUE.XLSX"] + [f for f in files if "CATALOGUE" not in f]
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
@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get('adminun'), request.cookies.get('admintkn'))
    adb.exit()
    if not istrue:
        return redirect("/admin-signin")
    if request.method == "POST":
        if "file" not in request.files:
            return redirect("/p")
        file = request.files['file']
        if file.filename == "":
            return redirect("/p")
        if file:
            file.save(os.path.join(app.root_path, "files", "LAST_UPLOADED.XLSX"))
            table.update_metatable("files/LAST_UPLOADED.XLSX")
            return redirect("/p?success=1")


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


@app.route("/p")
def panel():
    adb = AdminDatabase()
    istrue = adb.check_token(request.cookies.get('adminun'), request.cookies.get('admintkn'))
    adb.exit()
    if not istrue:
        return make_response(redirect("/admin-signin"))
    return send_from_directory("static", "tables.html")


@app.route("/_app_systems_of_size")
def _app_systems_of_size():
    return jsonify(
        ComputationsDbSession().systems_of_size(
            request.args["brand"], int(request.args["gender_int"]), request.args["standard"], request.args["size"]
        )
    )


@app.route("/_app_range_of_system")
def _app_range_of_system():
    return jsonify(
        ComputationsDbSession().range_of_system(
            request.args["brand"], int(request.args["gender_int"]), request.args["system"]
        )
    )


@app.route("/_app_recommended_size")
def _app_recommended_size():
    brand = request.args["brand"]
    gender_int = int(request.args["gender_int"])
    user_id = request.args["user_id"]
    s = ComputationsDbSession()
    # FIX IT !!!
    _recommended = ["UK", "4.5"]
    return jsonify(
        s.systems_of_size(brand, gender_int, *_recommended)
    )


@app.route("/_app_try_with_size")
def _app_try_with_size():
    user_id = request.args["user_id"]
    brand = request.args["brand"]
    size = request.args["size"]
    fit_value = request.args["fit_value"]
    s = FittingSession(user_id)
    s.try_with_size(brand, size, fit_value)
    return jsonify(dict(result="success"))


@app.route("/_app_my_collection")
def _app_my_collection():
    user_id = request.args["user_id"]
    s = FittingSession(user_id)
    ignore = int(request.args["ignore"])
    limit = None
    if request.args["limit"]:
        limit = int(request.args["limit"])
    media = "media" in request.args
    coll = s.get_user_collection(ignore, limit, media)
    # ...


'''
@app.route("/_app_download_photo")
def _app_download_photo():
    ...


@app.route("/_app_upload_photo")
def _app_upload_photo():
    ...


@app.route("/_app_ajax_brand_search")
def _app_ajax_brand_search():
    prefix = request.args["prefix"]
    ...
'''


@app.route("/error/<text>/<path:returnto>")
def throw_error(text, returnto):
    return render_template("error.html", text=text, returnto=returnto)


@app.route('/st/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route("/")
def welcome():
    return redirect("/error/Authorization needed/admin-signin")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
