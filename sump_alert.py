#!/usr/bin/env python3

from email.mime.text import MIMEText
import smtplib
import time

from sump_web import app, get_db


def send_alert(v):
    v = round(v, 1)
    subject = "ALERT: {} water depth is now at {} cm".format(app.config['NAME'], v)
    body = "{}'s average water depth over the past {} seconds is now at {} cm!"
    body = body.format(app.config['NAME'], app.config['CHECK_INTERVAL'], v)
    msg = MIMEText(body)
    msg['From'] = app.config['GMAIL_USERNAME']
    msg['To'] = ', '.join(app.config['ALERT_RECIPIENTS'])
    msg['Subject'] = subject
    gm = smtplib.SMTP('smtp.gmail.com', 587)
    gm.starttls()
    gm.ehlo()
    gm.login(app.config['GMAIL_USERNAME'], app.config['GMAIL_PASSWORD'])
    gm.send_message(msg)
    gm.quit()


if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        last_alert_time = 0
        while True:
            cur = db.execute("SELECT AVG(value) FROM data WHERE timestamp >= datetime('now', 'unixepoch') - ?", [app.config['CHECK_INTERVAL']])
            if cur.rowcount:
                avg = cur.fetchone()[0]
                if avg >= app.config['ALERT_DEPTH'] and int(time.time()) - app.config['CHECK_INTERVAL'] > last_alert_time:
                    try:
                        send_alert(avg)
                    except Exception as e:
                        print(e)
                    else:
                        last_alert_time = int(time.time())
            time.sleep(app.config['CHECK_INTERVAL'])
