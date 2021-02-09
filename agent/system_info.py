# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 09:51:43 2021

@author: Lucas Ramos Paiva
"""
import os
import platform
import subprocess
import re
import json
import distro

# Architecture
print("Architecture: " + platform.architecture()[0])

# machine
print("Machine: " + platform.machine())

# node (hostname)
#print("Node: " + platform.node())
print("Hostname: " + platform.uname()[1])

# system
print("System: " + platform.system())

# Uptime
# ----------------------------------------
# Gives a human-readable uptime string


def uptime():

    try:
        f = open("/proc/uptime")
        contents = f.read().split()
        f.close()
    except:
        return "Cannot open uptime file: /proc/uptime"

    total_seconds = float(contents[0])

    #  print(total_seconds)

    # Helper vars:
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    # Get the days, hours, etc:
    days = int(total_seconds / DAY)
    hours = int((total_seconds % DAY) / HOUR)
    minutes = int((total_seconds % HOUR) / MINUTE)
    seconds = int(total_seconds % MINUTE)

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    string += str(hours) + ":"
    string += str(minutes) + ":"
    string += str(seconds)

    return string


print("Uptime:", uptime())

# distribution (OS)
dist = distro.linux_distribution(full_distribution_name=False)
print("OS: " + dist)

# Kernel
print("Kernel: " + platform.release())

# CPU(s)


def get_processor_name():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).strip()
        for line in all_info.decode().split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line, 1)
    return ""


print("CPU(s):" + get_processor_name())

# Is service active ?

# service = "nginx"
# proc = subprocess.Popen(
#     ["systemctl", "is-active",  service], stdout=subprocess.PIPE)
# (output, err) = proc.communicate()
# output = output.decode('utf-8')

# print(service + ": " + output)


def isServiceActive(service):
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "ssh"])
    if (stat == 0):  # if 0 (active), print "Active"
        print(service + ": " + "active")


with open('config/config.json') as config_file:
    data = json.load(config_file)
    for service in data:
        isServiceActive(service)
