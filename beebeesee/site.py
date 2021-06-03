import json
import cv2
from flask import Blueprint, render_template, request
from .info import PRE_PATH, PROJECT_NAME, STATIC_DIR, VIEWS_DIR

site = Blueprint("site", PROJECT_NAME, template_folder=VIEWS_DIR)


@site.route("/", methods=["GET"])
def root():
    return render_template("root.html", pre_path=PRE_PATH)


@site.route("/__backdoor/videofeed", methods=["POST"])
def backdoor_videofeed():
    image = request.args.get("image")
    cv2.imshow("Test", image)
    cv2.destroyAllWindows()


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
