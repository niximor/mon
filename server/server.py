#!/usr/bin/env python3

from flask import Flask, render_template
import logging

from api import register_api
from website import register_site

app = Flask(__name__)
register_api(app)
register_site(app)

@app.route('/')
def index():
    return render_template("dashboard/index.html")

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s {%(filename)s:%(funcName)s:%(lineno)s}",
        level=logging.DEBUG
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    app.run(debug=True, host='0.0.0.0', processes=10)
