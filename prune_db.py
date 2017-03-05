#!/usr/bin/env python3

# Remove all data entries older than 24h
# cron example:
# 0 0 * * * prune_db.py



import time

from sump_web import app, get_db


if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        db.execute('DELETE FROM data WHERE timestamp <= ?', [int(time.time()) - 86400])
        db.execute('VACUUM')
        db.commit()
