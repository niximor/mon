from flask import Flask
from config import config

from website.settings import settings
from website.probe import probe
import jinja2


def register_site(app: Flask):
    app.register_blueprint(settings, url_prefix="/settings")
    app.register_blueprint(probe, url_prefix="/probe")

    @app.context_processor
    def inject_probes():
        return {
            "probes_list": config.api.get("/probe", {"show": ["name", "errors", "warnings"]})
        }

    @jinja2.contextfunction
    def get_context(c):
        return c

    @app.context_processor
    def inject_debug():
        return {
            "context": get_context,
            "callable": callable
        }
