# mon
Lightweight monitoring platform

The platform consists of three basic parts:
- Server
- Probe
- Services

## Server
Server is the main core of the whole monitoring. It is based on Python-Flask and MySQL, provides monitoring and configuration web interface and API for other parts of the system.

## Probe
Probe is lightweight client to the server. Probe is to be installed on monitored systems and the probe itself runs the checks. It communicates (passively) with the server API.

## Services
The monitoring plugins itself. Each service is an executable file, that provides its own configuration and does the checks.
