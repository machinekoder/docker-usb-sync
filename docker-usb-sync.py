#!/usr/bin/env python3

import syslog
import subprocess
import os
import grp


def log(message):
    print(message)
    syslog.syslog(message)


def exec_in_container(cmd, name="ros-devel"):
    return subprocess.check_output(
        "docker exec {} bash -c '{}'".format(name, cmd),
        universal_newlines=True,
        shell=True,
    )


root_dev = "/dev/bus/usb"

bus_paths = ["/dev"]
for bus_num in os.listdir(root_dev):
    bus_paths.append(os.path.join(root_dev, bus_num))

for bus_path in bus_paths:
    container_devices = exec_in_container("ls " + bus_path).split("\n")
    host_devices = os.listdir(bus_path)

    # remove dead links
    for device in container_devices:
        if device and device not in host_devices:
            exec_in_container("rm " + os.path.join(bus_path, device))

    # add new links
    for device in host_devices:
        host_device_path = os.path.join(bus_path, device)
        if os.path.isdir(host_device_path):
            continue
        if device not in container_devices:
            device_path = os.path.join(bus_path, device)

            if os.path.islink(host_device_path):
                source = os.readlink(host_device_path)
                cmd = "ln -s {source} {device}".format(
                    source=source, device=device_path
                )
                exec_in_container(cmd)
                continue

            stat = os.stat(host_device_path)
            cmd = "mknod {device} c {major} {minor}".format(
                device=device_path,
                major=os.major(stat.st_rdev),
                minor=os.minor(stat.st_rdev),
            )
            exec_in_container(cmd)
            group = grp.getgrgid(stat.st_gid).gr_name
            cmd = "chgrp {group} {device}".format(group=group, device=device_path)
            exec_in_container(cmd)
            cmd = "chmod {mode} {device}".format(
                mode="%o" % (stat.st_mode & 0o777), device=device_path
            )
            exec_in_container(cmd)
