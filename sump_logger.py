#!/usr/bin/env python3

import time

import serial

from sump_web import app, get_db


if __name__ == '__main__':
    with app.app_context():
        time.sleep(5)
        db = get_db()
        ser = serial.Serial(app.config['SERIAL_DEVICE'], 115200)
        while True:
            rdg = int(ser.readline().decode().strip())
            # print(rdg)
            values = (int(time.time()), rdg)
            db.execute("INSERT INTO data values(?, ?)", values)
            db.commit()
            time.sleep(1)
