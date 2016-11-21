"""
Mon server abstraction.
"""

from typing import Dict, List
import socket
import logging
from datetime import datetime

from lib.client import Client
from service import Service, ServiceMapping


class Server:
    def __init__(self, address):
        self.client = Client(address)
        self.probe_name = socket.gethostname()
        self.services = None

    def register_probe(self, services: Dict[str, Service]) -> None:
        """
        Register the probe on startup or reconfiguration.
        :param services: List of services that this probe is able to provide.
        """
        self.services = services
        self.client.put("probe", json={
            "name": self.probe_name,
            "services": [
                {
                    "name": service.name,
                    "description": service.description,
                    "options": [
                        {
                            "identifier": option_identifier,
                            "name": option["name"],
                            "type": option["type"],
                            "description": option.get("description", ""),
                            "required": option.get("required", False),
                        } for option_identifier, option in service.options.items()
                    ],
                    "thresholds": {
                        reading: {
                            "status": status,
                            "min": values.get("min"),
                            "max": values.get("max")
                        } for reading, statuses in service.thresholds.items() for status, values in statuses.items()
                    }
                } for service in services.values()
            ]
        })

    def get_mapped_services(self) -> List[ServiceMapping]:
        """
        Return list of mapped services.
        :return:
        """
        mappings = self.client.get("services/%s" % (self.probe_name, ), params={
            "show": ["id", "name", "service", "options.identifier", "options.value"]
        })

        out = []
        for mapping in mappings:
            if mapping["service"] in self.services:
                out.append(ServiceMapping(
                    mapping["id"],
                    self.services[mapping["service"]],
                    {
                        option["identifier"]: option["value"]
                        for option in mapping["options"] if option["value"] is not None
                    },
                    mapping["name"]
                ))

        return out

    def update(self, fetch_result: dict, time_point: datetime=None) -> None:
        """
        Post new values fetched from services.
        :param fetch_result: Result of fetched services.
        :param time_point: Point in time when the fetch was taken.
        :return:
        """
        logging.info("Update readings for %s:" % (time_point.strftime("%Y-%m-%d %H:%M:%S")))

        # Build up readings to post to server.
        readings = []

        for mapping, values in fetch_result.items():
            for key, val in values.items():
                readings.append({
                    "service": mapping,
                    "reading": key,
                    "value": int(val),
                    "timestamp": time_point.isoformat()
                })
                logging.debug("    Service %d %s=%s" % (mapping, key, val))

        self.client.put("/readings/%s" % (self.probe_name, ), json=readings)
