from datetime import datetime
import io
import random
import sqlite3
import time


from flask import Flask, g, make_response
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def create_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', 'r') as f:
            s = f.read()
            print(s)
            db.executescript(s)
            db.commit()

def populate_test_data():
    import time
    import random
    with app.app_context():
        db = get_db()
        st = int(time.time()) - 86400
        for t in range(86400):
            db.execute('INSERT INTO data VALUES(?, ?)', (st + t, random.randint(20, 40)))
        db.commit()


@app.route('/img/chart24h.png')
def gen_chart():
    db = get_db()
    x = []
    y = []
    for i, row in enumerate(db.execute(
        "SELECT * FROM data WHERE timestamp >= ? - 86400", [int(time.time())])):
        if i % 60 == 0:
            x.append(datetime.fromtimestamp(row[0]))
            y.append(row[1])
    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(x, y)
    plt.title('Sump Pump Water Level (last 24 hours)')
    ax.set_xlabel('Time')
    ax.set_ylabel('Water level (cm)')
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
    ax.xaxis.set_major_locator(mdates.HourLocator())
    stream = io.BytesIO()
    fig.savefig(stream, format='png')
    stream.seek(0)
    response = make_response(stream.read())
    response.headers['Content-Type'] = 'image/png'
    return response