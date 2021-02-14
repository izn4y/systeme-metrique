import traceback
import platform
import subprocess
import re
import json
import distro
import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


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


# Distribution
dist = distro.linux_distribution(full_distribution_name=False)
distInfo = dist[0] + " " + dist[1] + " " + dist[2]

data = {"architecture": platform.architecture()[0], "machine": platform.machine(), "uptime_host": uptime(),
        "hostname": platform.uname()[1], "system": platform.system(), "distro_host": distInfo,
        "kernel": platform.release(), "processor": get_processor_name()}

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'bdd.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
bdd = SQLAlchemy(app)
# Init Marshmallow
ma = Marshmallow(app)


class Metrics(bdd.Model):
    id = bdd.Column(bdd.Integer, primary_key=True)
    architecture = bdd.Column(bdd.String(200))
    machine = bdd.Column(bdd.String(200))
    uptime_host = bdd.Column(bdd.String(200))
    hostname = bdd.Column(bdd.String(200))
    system = bdd.Column(bdd.String(200))
    distro_host = bdd.Column(bdd.String(200))
    kernel = bdd.Column(bdd.String(200))
    processor = bdd.Column(bdd.String(200))

    def __init__(self, architecture, machine, uptime_host, hostname, system, distro_host, kernel, processor):
        self.architecture = architecture
        self.machine = machine
        self.uptime_host = uptime_host
        self.hostname = hostname
        self.system = system
        self.distro_host = distro_host
        self.kernel = kernel
        self.processor = processor


# Metriques Schema
class MetricsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'architecture', 'machine', 'uptime_host', 'hostname',
                  'system', 'distro_host', 'kernel', 'processor')


@app.route('/api/push_host_infos/', methods=['GET', 'POST'])
def push_host_infos():
    architecture = data["architecture"]
    machine = data["machine"]
    uptime_host = data["uptime_host"]
    hostname = data["hostname"]
    system = data["system"]
    distro_host = data["distro_host"]
    kernel = data["kernel"]
    processor = data["processor"]

    new_metrics = Metrics(architecture, machine, uptime_host, hostname, system, distro_host, kernel, processor)

    bdd.session.add(new_metrics)
    bdd.session.commit()
    return metrics_schema.jsonify(new_metrics)


@app.route('/', methods=['GET'])
def index():
    all_metrics = Metrics.query.all()
    result = all_metrics.fetchall()
    print(result)
    # for metrics in all_metrics:
    #     print(metrics)
    return render_template('metrics.html', data=all_metrics)


# Init Schema
metrics_schema = MetricsSchema()



# Run Server
if __name__ == '__main__':
    app.run(debug=True)
