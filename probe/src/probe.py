#!/usr/bin/env python3

import signal
from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime

from service import Service
from lib.server import Server

import logging
import time

# Whether the probe should quit.
quit_flag = False

# Whether the probe should reload.
hup_flag = True


def sig_handler(sig_num: int, _) -> None:
    """
    Signal handler that sets proper flags of events signaled by the signal subystem to the Probe.
    :param sig_num: Number of signal registered to this callback.
    :param _: Stack frame is not needed.
    """
    global quit_flag, hup_flag

    if sig_num in (signal.SIGINT, signal.SIGTERM):
        quit_flag = True
    elif sig_num in (signal.SIGHUP, ):
        hup_flag = True


def safe_register_signal(sig_num: int) -> None:
    """
    Safe register signal, does not throw any exception if the signal registration fails.
    :param sig_num: Signal number.
    """
    try:
        signal.signal(sig_num, sig_handler)
    except AttributeError:
        pass
    except ValueError:
        pass


def register_signals() -> None:
    """
    Register signals the Probe can handle.
    """
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    safe_register_signal(signal.SIGHUP)
    safe_register_signal(signal.SIGUSR1)
    safe_register_signal(signal.SIGUSR2)


def sleep():
    time.sleep(60)


def main():
    """
    Main.
    :return:
    """
    global hup_flag, quit_flag

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s {%(filename)s:%(funcName)s:%(lineno)s}",
        level=logging.DEBUG
    )

    register_signals()

    parser = ArgumentParser()
    parser.add_argument("-f", "--config", help="Config file", default="/etc/mon/probe.conf", dest="config")

    args = parser.parse_args()

    server = None

    while not quit_flag:
        if hup_flag:
            try:
                cf = ConfigParser()
                try:
                    cf.read_file(open(args.config, "r"), args.config)
                except FileNotFoundError as e:
                    logging.error("Config file '%s' was not found. Not reconfiguring." % (e.filename, ))
                    continue

                server = Server(cf.get("server", "Address"))

                services = Service.scan(cf.get("probe", "services"))
                server.register_probe(services)

            finally:
                hup_flag = False

        if server:
            mapped = server.get_mapped_services()
            responses = {}

            time_point = datetime.now()

            for service in mapped:
                responses[service.id] = service.fetch()

            server.update(responses, time_point)

        sleep()

if __name__ == "__main__":
    main()
