#!/usr/bin/env python3

from sump_web import app, get_db


if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', 'r') as f:
            s = f.read()
            print(s)
            db.executescript(s)
            db.commit()