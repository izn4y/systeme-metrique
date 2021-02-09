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

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

data = {}

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


# Architecture
print("Architecture: " + platform.architecture()[0])
data["archicteture"] = platform.architecture()[0]
# machine
print("Machine: " + platform.machine())
data["machine"] = platform.machine()

# node (hostname)
print("Hostname: " + platform.uname()[1])
data["hostname"] = platform.uname()[1]

# system
print("System: " + platform.system())
data["system"] = platform.system()

# Uptime
print("Uptime:", uptime())
data["uptime"] = uptime()

# distribution (OS)
dist = distro.linux_distribution(full_distribution_name=False)
distInfo = dist[0] + " " + dist[1] + " " + dist[2]
print(distInfo)
data["distro"] = distInfo

# Kernel
print("Kernel: " + platform.release())
data["kernel"] = platform.release()


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
data["processor"] = get_processor_name()


def isServiceActive(service):
    stat = subprocess.call(["systemctl", "is-active", "--quiet", "ssh"])
    if (stat == 0):  # if 0 (active), print "Active"
        print(service + ": " + "active")
        data["ActiveServices"].append(service)


with open('config.json') as config_file:
    conf = json.load(config_file)
    data["ActiveServices"] = []
    for service in conf:
        isServiceActive(service)

with open("data_file.json", "w") as write_file:
    json.dump(data, write_file)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@cross_origin()
@app.route('/api/push_host_infos/', methods=['GET', 'POST'])
def push_host_infos():
    try:
        data = request.data
        print(data)
        result = 'OK'
    except Exception:
        return jsonify('Error\n%s' % traceback.format_exc())
    return jsonify(result)


@app.route('/api/get-json')
def system_info():

    return jsonify(data)


if __name__ == '__main__':
    print("Application en écoute sur port 8517")
    app.run(host="0.0.0.0", port=int("8517"))
