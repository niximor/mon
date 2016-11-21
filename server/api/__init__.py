from flask import Flask
from flask_restful import Api
from api.probe import Probe, Probes
from api.services import Services
from api.readings import Readings

api = Api(prefix="/api/v1")
api.add_resource(Probes, "/probe/")
api.add_resource(Probe, "/probe/<string:name>/")
api.add_resource(Services, "/services/<string:probe_name>/")
api.add_resource(Readings, "/readings/<string:probe_name>/")


def register_api(app: Flask):
    """
    Register API to the Flask app.
    """
    # noinspection PyTypeChecker
    api.init_app(app)
