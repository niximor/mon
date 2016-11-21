"""
Mon settings.
"""

from flask import Blueprint, render_template, redirect, url_for, request, abort
from config import config

settings = Blueprint("settings", __name__)


@settings.route("/")
def index():
    """
    Default target, that redirects.
    """
    return redirect(url_for("settings.probes"))


@settings.route("/probes/")
def probes():
    """
    List of probes to configure.
    """
    return render_template("settings/index.html",
                           probes=config.api.get("probe", {"show": ["name", "num_services", "num_mapped"]}))


@settings.route("/probes/<probe>/services/")
def services(probe):
    """
    List of mapped services of a probe.
    """
    return render_template("settings/services.html",
                           probe=config.api.get("probe/%s" % (probe, )),
                           services=config.api.get("services/%s" % (probe, ), params={
                               "show": ["id", "name", "description", "service", "status", "error_cause"],
                               "status": "all"
                           }))


@settings.route("/probes/<probe>/services/map", methods=["GET", "POST"])
@settings.route("/probes/<probe>/services/map/<service>")
def map_service(probe, service=None):
    """
    Map new service in a two step form. First, select service to be mapped, second, fill in service options.
    """
    probe = config.api.get("probe/%s" % (probe, ))

    if request.method == "POST":
        option_names = request.form.getlist("option")
        values = request.form.getlist("value")

        if len(option_names) != len(values):
            abort(400)

        config.api.put("services/%s" % (probe["name"], ), json=[{
            "name": request.form["name"],
            "service": request.form["service"],
            "options": {
                option_names[i]: values[i] for i in range(0, len(option_names))
            }
        }])

        return redirect(url_for(".services", probe=probe["name"]))

    if service is not None:
        service_dict = None
        for s in probe["services"]:
            if s["name"] == service:
                service_dict = s
                break

        if service_dict is None:
            abort(404)

        return render_template("settings/map_service_options.html", probe=probe, service=service_dict)
    else:
        return render_template("settings/map_service.html", probe=probe)


@settings.route("/probes/<probe>/services/modify/<int:db_id>", methods=["GET", "POST"])
def modify_mapping(probe, db_id):
    """
    Modify service mapping options.
    """
    probe = config.api.get("probe/%s" % (probe,))

    if request.method == "POST":
        # Build patch request for the API.

        option_names = request.form.getlist("option")
        values = request.form.getlist("value")

        if len(option_names) != len(values):
            abort(400)

        service_data = [{
            "id": db_id,
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "options": {
                option_names[i]: values[i] for i in range(0, len(option_names)) if values[i] != ""
            }
        }]

        config.api.patch("services/%s" % (probe["name"], ), json=service_data)
        return redirect(url_for(".services", probe=probe["name"]))
    else:
        return render_template("settings/modify_mapping.html",
                               probe=probe,
                               service=config.api.get("services/%s" % (probe["name"], ), params={
                                    "id": db_id,
                                    "show": ["id", "name", "description", "service", "options.name",
                                             "options.identifier", "options.description", "options.value",
                                             "options.required", "options.type"],
                                    "status": "all"
                                })[0])


@settings.route("/probes/<probe>/services/status/<int:db_id>")
def toggle_status(probe, db_id):
    """
    Toggle between active and suspended services.
    """
    service = config.api.get("services/%s" % (probe, ), params={
        "id": db_id,
        "show": "status",
        "status": "all"
    })[0]

    new_status = None

    if service["status"] == "active":
        new_status = "suspended"
    elif service["status"] == "suspended":
        new_status = "active"

    if new_status is not None:
        config.api.patch("services/%s" % (probe, ), json=[{
            "id": db_id,
            "status": new_status
        }])

    return redirect(url_for(".services", probe=probe))


@settings.route("/probes/<probe>/services/delete/<int:db_id>")
def delete_mapping(probe, db_id):
    """
    Delete service mapping.
    """
    config.api.delete("services/%s" % (probe, ), params={
        "id": db_id
    })
    return redirect(url_for(".services", probe=probe))
