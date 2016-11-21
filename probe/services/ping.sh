#!/bin/bash

# Simple ping service for MON probe.

case "$1" in
    config)
        cat <<EOF
description=Ping specific host and return 1 if host is available and 0 if it is not.

[thresholds]
*.error.min=0
*.error.max=0

[options]
hostname=Host to ping (IP or hostname)
hostname.type=string
hostname.description=Enter hostname or IP address (can be both IPv4 and IPv6) of remote server to ping.
hostname.required=1
timeout=Ping timeout [s]
timeout.type=integer
timeout.description=Number of seconds to wait for ping before deciding the host is dead. Default = 1s.
timeout.default=1
EOF
        ;;

    *)
        fping -q -t $(($TIMEOUT * 1000)) $HOSTNAME
        if [ $? -eq 0 ]; then
            echo "ping=1"
        else
            echo "ping=0"
        fi
        ;;
esac
