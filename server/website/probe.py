from flask import Blueprint, render_template

probe = Blueprint("probe", __name__)


@probe.route("/<name>")
def index(name):
    return render_template("probe/index.html")
