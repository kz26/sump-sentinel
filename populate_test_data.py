#!/usr/bin/env python3

from sump_web import app, get_db

import time
import random


if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        st = int(time.time()) - 86400
        for t in range(86400):
            db.execute('INSERT INTO data VALUES(?, ?)', (st + t, random.randint(20, 40)))
        db.commit()