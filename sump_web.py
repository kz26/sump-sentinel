from datetime import datetime
import io
import random
import sqlite3
import time

from version import __version__

from flask import Flask, abort, g, jsonify, make_response, render_template

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html',
        version=__version__,
        sump_depth=app.config['SUMP_DEPTH'],
        alert_depth=app.config['ALERT_DEPTH']
    )


@app.route('/img/chart24h.png')
def gen_chart():
    db = get_db()
    x = []
    y = []
    for i, row in enumerate(db.execute(
        "SELECT timestamp, ?-value FROM data WHERE timestamp >= ? - 86400",
            [app.config['SUMP_DEPTH'], int(time.time())])):
        if row and i % 60 == 0:
            x.append(datetime.fromtimestamp(row[0]))
            y.append(row[1])
    if x and y:
        fig, ax = plt.subplots(figsize=(20, 5))
        ax.plot(x, y)
        plt.title('Sump Pump Water Level (last 24 hours)')
        ax.set_xlabel('Time')
        ax.set_ylabel('Water level (cm)')
        ax.set_ylim(bottom=0)
        fig.autofmt_xdate()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d %-I %p'))
        ax.xaxis.set_major_locator(mdates.HourLocator())
        stream = io.BytesIO()
        fig.savefig(stream, format='png')
        stream.seek(0)
        response = make_response(stream.read())
        response.headers['Content-Type'] = 'image/png'
        return response
    else:
        abort(404)


@app.route('/latest')
def latest_reading():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT timestamp AS timestamp, round(?-value, 1) AS value FROM data ORDER BY timestamp DESC LIMIT 1", [app.config['SUMP_DEPTH']])
    res = c.fetchone()
    if res:
        return jsonify({k: res[k] for k in res.keys()})
    else:
        return jsonify(None)
