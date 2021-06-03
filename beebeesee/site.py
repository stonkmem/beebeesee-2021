from flask import Blueprint, render_template
from .info import PROJECT_NAME, VIEWS_DIR

site = Blueprint("site", PROJECT_NAME, template_folder=VIEWS_DIR)


@site.route("/", methods=["GET"])
def root():
    return render_template("root.html")
