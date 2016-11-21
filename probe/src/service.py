"""
Service.
"""

from subprocess import check_output, CalledProcessError
from configparser import ConfigParser, DuplicateOptionError, DuplicateSectionError
from typing import Dict
from os import environ

import os
import logging


class Service:
    """
    A Service is an executable script that can be called multiple ways.
    Calling `service.exe config` should return service configuration.
    The configuration has following form:

        description = Ping specific hosts.  # Service description

        [options]                           # Service-defined configuration options for the website.
        hostnames = List of host names.     # Option identifier (here hostnames) followed by service human readable name
        hostnames.type = list               # Option data type. Default is string, and can be:
                                                string, int, double, boolean, list
        hostnames.description               # Option description that is shown when configuring the option.
        timeout = Ping timeout              # Another option.

    Calling `service.exe fetch` should return current service metrics.
    """
    def __init__(self, binary: str):
        self.binary = binary
        self.options = {}
        self.thresholds = {}
        self.name = os.path.splitext(os.path.basename(self.binary))[0]
        self.description = ""

        self.logger = logging.getLogger("services.%s" % (self.name, ))

        self.get_config()

        self.logger.debug("Discovered service %s with following options:" % (self.name, ))
        for option, setup in self.options.items():
            self.logger.debug("  - %s" % (option, ))
            for key, val in setup.items():
                self.logger.debug("        %s = %s" % (key, val))

    @staticmethod
    def scan(path: str) -> Dict[str, "Service"]:
        """
        Recursively scan given path for service executables.
        :param path: Path to scan.
        :return: List of found services.
        """
        out = {}

        try:
            for file in os.scandir(path):
                if file.name.startswith("."):
                    continue

                if file.is_file():
                    service = Service.examine_file(file.path)
                    if isinstance(service, Service):
                        out[service.name] = service

                elif file.is_dir():
                    out.update(Service.scan(file.path))
        except FileNotFoundError as e:
            logging.error("Services directory '%s' was not found." % (e.filename, ))

        return out

    @staticmethod
    def examine_file(file_path: str) -> "Service":
        """
        Examine one file whether it could be service. Return that service if possible. Otherwise, returns None.
        :param file_path: Full path to the file to be examined.
        :return: Service instance or None if the file cannot be service.
        """
        if os.access(file_path, os.X_OK):
            return Service(file_path)
        return None

    def get_config(self) -> None:
        """
        Get config from service, which is then used to configure the service on the website.
        """
        config = "[config]\n" + check_output([self.binary, "config"]).decode("utf-8")
        parser = ConfigParser(allow_no_value=True, delimiters=("=", ), inline_comment_prefixes=("#", ),
                              empty_lines_in_values=False, default_section=None)

        try:
            parser.read_string(config, source=self.binary)

            self.description = parser.get("config", "description", fallback="")

            if parser.has_section("options"):
                # Populate self.options.
                self.populate_options(parser)

            if parser.has_section("thresholds"):
                self.populate_thresholds(parser)

        except DuplicateSectionError as e:
            self.logger.error("Duplicate section '%s' in service config. Service skipped." % (e.section, ))
            return
        except DuplicateOptionError as e:
            self.logger.error("Duplicate option '%s.%s' in service config. Service skipped." % (e.section, e.option, ))
            return

    def populate_options(self, parser: ConfigParser) -> None:
        """
        Populate self.options dict with service options as defined by config.
        :param parser: ConfigParser containing parsed options from the service.
        """
        for full_option in parser.options("options"):
            value = parser.get("options", full_option)

            split = full_option.split(".")

            if len(split) > 1:
                option = ".".join(split[:-1])
                subitem = split[-1]

                # We know only type and description subitems. Treat anything else as part of item name.
                if subitem not in ("type", "description", "required", "default"):
                    option += ".%s" % subitem
                    subitem = "name"
            else:
                option = full_option
                subitem = "name"

            if subitem == "required":
                value = True if value == "1" else False

            self.options.setdefault(option, {
                "name": option,
                "type": "string",
                "required": False,
            })[subitem] = value

    def populate_thresholds(self, parser: ConfigParser) -> None:
        """
        Fill in self.thresholds from service configuration:
            self.thresholds[reading][status] = {"min": None or value, "max": None or value}
        :param parser: ConfigParser with service options.
        """
        for full_option in parser.options("thresholds"):
            split = full_option.split(".")
            if len(split) < 3 or split[-1] not in ("min", "max"):
                self.logger.error("Threshold item '%s' has invalid name. "
                                  "It must be in form {reading}.{status}.(min|max)." % (full_option, ))
                continue

            min_max = split[-1]
            status = split[-2]
            reading = ".".join(split[:-2])

            self.thresholds\
                .setdefault(reading, {})\
                .setdefault(status, {"min": None, "max": None})[min_max] = parser.getint("thresholds", full_option)


class ServiceMapping:
    """
    Mapping of service with options for fetching the data.
    """
    def __init__(self, id_, service, options, name=None):
        self.id = id_
        self.name = name
        self.service = service
        self.options = options

    def fetch(self):
        """
        Execute the service and fetch the results.
        :return:
        """
        env = environ.copy()

        env.update({
            name.upper(): self.options.get(name, option.get("default", ""))
            for name, option in self.service.options.items()
        })

        self.service.logger.debug("Fetching service %s with configuraton:" % (self.service.name, ))
        for key, val in env.items():
            self.service.logger.debug("    - %s=%s" % (key, val))

        try:
            output = check_output([self.service.binary, "fetch"], env=env)
            result = "[fetch]\n" + output.decode("utf-8")

            parser = ConfigParser(allow_no_value=True, delimiters=("=", ), inline_comment_prefixes=("#", ),
                                  empty_lines_in_values=False, default_section=None)
            parser.read_string(result)

            return {
                option: parser.get("fetch", option)
                for option in parser.options("fetch")
            }
        except CalledProcessError as e:
            if e.output:
                logging.error(e.output)
            logging.error("Service %s returned nonzero exit code %d." % (self.service.name, e.returncode))
