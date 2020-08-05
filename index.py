#!/usr/bin/python3

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import request
from flask import send_from_directory

import admin
import os
import photos
import table
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
    adb = admin.AdminDatabase()
    token = adb.get_token(username, pwd)
    adb.exit()
    resp = make_response(redirect("/p" if token != "notoken" else "/admin-signin"))
    resp.set_cookie('adminun', username)
    resp.set_cookie('admintkn', token)
    return resp


@app.route("/current_table<int:randomid>.xlsx")
def download(randomid):
    adb = admin.AdminDatabase()
    istrue = adb.check_token(request.cookies.get('adminun'), request.cookies.get('admintkn'))
    adb.exit()
    if not istrue:
        return make_response(redirect("/admin-signin"))
    rn = random.randrange(111111, 999999)
    table.build_table("files/ADMIN_TABLE_%d.XLSX" % rn)
    return send_from_directory("files", "ADMIN_TABLE_%d.XLSX" % rn)


@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():
    adb = admin.AdminDatabase()
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


@app.route("/p")
def panel():
    adb = admin.AdminDatabase()
    istrue = adb.check_token(request.cookies.get('adminun'), request.cookies.get('admintkn'))
    adb.exit()
    if not istrue:
        return make_response(redirect("/admin-signin"))
    return send_from_directory("static", "tables.html")


@app.route('/st/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
