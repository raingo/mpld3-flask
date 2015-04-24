from flask import Flask, render_template, json, request
import numpy as np

import matplotlib
import json
import random

import os

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

from threading import Lock
lock = Lock()
import datetime
import mpld3
from mpld3 import plugins

# Setting up matplotlib sytles using BMH
s = json.load(open("./static/bmh_matplotlibrc.json"))
matplotlib.rcParams.update(s)

x = range(100)
y = [a * 2 + random.randint(-20, 20) for a in x]

pie_fracs = [20, 30, 40, 10]
pie_labels = ["A", "B", "C", "D"]

import re
iter_pattern = re.compile(r'Iteration (\d+), Testing net')
res_pattern = re.compile(r'Test net output #(\d+): (\S+) = ([\d\.]+)')

iter_pattern2 = re.compile(r'Iteration (\d+), loss = ([\d\.]+)')

def load_log2(log_path):

    iter_loss = []
    with open(log_path) as reader:
        while True:
            line = reader.readline()
            if not line:
                break
            m = iter_pattern2.search(line)
            if m:
                iter_loss.append((int(m.group(1)), 'loss', float(m.group(2))))

    return iter_loss


def load_res(reader, res, iter):
    while True:
        line = reader.readline()
        m = res_pattern.search(line)

        if not m:
            break

        if 'top' not in m.group(2):
            continue
        res.append((iter, m.group(2), float(m.group(3))))

def load_log(log_path):

    iter_loss = []
    with open(log_path) as reader:
        while True:
            line = reader.readline()
            if not line:
                break

            m = iter_pattern.search(line)
            if m:
                load_res(reader, iter_loss, int(m.group(1)))

    return iter_loss


def draw_fig(logpath, type):
    """Returns html equivalent of matplotlib figure

    Parameters
    ----------
    fig_type: string, type of figure
            one of following:
                    * line
                    * bar

    Returns
    --------
    d3 representation of figure
    """

    n_points = 1000

    with lock:

        if type == 'acc':
            xNy = load_log(logpath)
        elif type == 'loss':
            xNy = load_log2(logpath)
        else:
            return "log type not found"

        names = set([n for _, n, _ in xNy])
        fig, ax = plt.subplots()
        for name in names:
            xy = [(x, y) for x, n, y in xNy if n == name]
            x = [f[0] for f in xy]
            y = [f[1] for f in xy]

            n = len(x)
            intv = max(1, n / n_points)

            ax.plot(x[::intv], y[::intv], label = name)
        #print len(names)
        ax.legend(loc = 'best')


    return mpld3.fig_to_html(fig)

app = Flask(__name__)


@app.route('/')
def home(path=""):
    logpath = request.args.get('q', '')
    return render_template('index.html', default=logpath)


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    logpath = data['logpath']
    type = data['type']

    #print logpath, type

    if os.path.exists(logpath):
        return draw_fig(logpath, type)
    return "not found"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8081)
