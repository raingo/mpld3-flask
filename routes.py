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
loss_pattern = re.compile(r'Iteration (\d+), loss = ([\d\.]+)')

def load_log(log_path):

    iter_loss = []
    with open(log_path) as reader:
        for line in reader:
            m = loss_pattern.search(line)
            if m:
                iter_loss.append((int(m.group(1)), float(m.group(2))))

    return iter_loss


def draw_fig(logpath):
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

    n_points = 100

    with lock:
        fig, ax = plt.subplots()

        xy = load_log(logpath)
        x = [f[0] for f in xy]
        y = [f[1] for f in xy]

        n = len(x)
        intv = n / n_points

        ax.plot(x[::intv], y[::intv])


    return mpld3.fig_to_html(fig)

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    logpath = data['logpath']

    print logpath

    if os.path.exists(logpath):
        return draw_fig(logpath)
    return "not found"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
