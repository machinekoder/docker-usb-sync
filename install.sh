#!/bin/bash -xe
if [ ! "$BASH_VERSION" ]; then
    echo "Warning: this script should be executed with bash"
    exec /bin/bash "$0"
fi
cd "$(dirname "${BASH_SOURCE[0]}")"

sudo cp docker-usb-sync.py /usr/bin/docker_device_sync.py
sudo cp 90-docker-usb-sync.rules /etc/udev/rules.d/
sudo service udev restart
