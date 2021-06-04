import os
import json
from pathlib import Path
from typing import *
import cv2
from flask import (
    Blueprint,
    render_template,
    request, flash,
    redirect,
    url_for,
    session
)
from werkzeug.utils import secure_filename
from .brain import predict
from .info import PRE_PATH, PROJECT_NAME, STATIC_DIR, VIEWS_DIR, UPLOAD_DIR
from .util.fr import open_image

site = Blueprint("site", PROJECT_NAME, template_folder=VIEWS_DIR)


@site.route("/", methods=["GET"])
def root():
    return render_template("root.html", pre_path=PRE_PATH)


@site.route("/success", methods=["GET"])
def success():
    return render_template("success.html")


"""
@site.route("/testing", methods=["GET"])
def testing():
    return render_template("pullmyhair.html")


@site.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        print(request.form)
        return jsonify(request.form['userID'], request.form['file'])
    return render_template('signup.html')
"""


@site.route("/analyzer", methods=['GET', 'POST'])
def analyzer():
    ALLOWED_EXTS: Set[str] = {".png", ".jpg", ".jpeg"}

    def file_check(filename: str) -> bool:
        p = Path(filename)
        return p.suffix in ALLOWED_EXTS
    if request.method == "POST":
        if "myfile" not in request.files:
            flash("No file part.")
            return redirect(request.url)
        file = request.files["myfile"]
        if file.filename == "":
            flash("No selected file.")
            return redirect(request.url)
        ok = file_check(file.filename)
        if file and ok:
            filename = secure_filename(file.filename)
            end_path = UPLOAD_DIR / filename
            file.save(end_path)
            print("CHECKPOINT 1")
            emotion = predict(open_image(end_path))
            print("CHECKPOINT 2")
            session["analyzer_emotion"] = emotion
            os.remove(end_path)
            return redirect(url_for("site.analyzer_success"))
        else:
            return redirect(request.url)
    elif request.method == "GET":
        return render_template("analyzer.html")


@site.route("/analyzer/success", methods=["GET"])
def analyzer_success():
    if "analyzer_emotion" not in session:
        return redirect(url_for("site.lostpage", lost="you-idiot"))
    emotion = session["analyzer_emotion"]
    session.pop("analyzer_emotion")
    return render_template("analyzer-success.html", emotion=emotion)



@site.route("/__backdoor/videofeed", methods=["POST"])
def backdoor_videofeed():
    print(request.form["file"])


@site.route("/_model/model", methods=["GET"])
def _model_model():
    MODEL_PATH = STATIC_DIR / "model" / "model.json"
    model = json.load(MODEL_PATH.open("r"))
    return model


@site.route("/_model/<filename>", methods=["GET"])
def _model_file(filename):
    filepath = STATIC_DIR / "model" / filename
    with filepath.open("rb") as f:
        data = f.read()
    return data


@site.route("/<lost>/")
def lostpage(lost):
    return """
<script>
alert("Are you sure this page really exists? We can't seem to find it.")
</script><h1>
<a href="/">Visit our app!</a></h1>
"""
