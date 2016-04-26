import flask
from flask import Flask
from flask import render_template
from flask import request

from email.Parser import HeaderParser
import email.utils

from datetime import datetime
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['headers'].strip()
        r = {}
        n = HeaderParser().parsestr(data)
        graph = [['Hop', 'Delay',]]
        c = len(n.get_all('Received'))
        for i in range(len(n.get_all('Received'))):
            line = n.get_all('Received')[i].split(';')
            try:
                next_line = n.get_all('Received')[i+1].split(';')
            except IndexError:
                next_line = None
            org_time = email.utils.mktime_tz(email.utils.parsedate_tz(line[-1]))
            if not next_line:
                next_time = org_time
            else:
                next_time = email.utils.mktime_tz(email.utils.parsedate_tz(next_line[-1]))
            if line[0].startswith('from'):
                data = re.findall('from\s+(.*?)\s+by(.*?)(?:(?:with|via)(.*?)(?:id|$)|id)', line[0], re.DOTALL)
            else:
                data = re.findall('()by(.*?)(?:(?:with|via)(.*?)(?:id|$)|id)', line[0], re.DOTALL)

            delay = org_time - next_time
            if delay < 0:
                delay = 0

            r[c] = {
                'Timestmp': org_time,
                'Time': datetime.fromtimestamp(org_time).strftime('%m/%d/%Y %I:%M:%S %p'),
                'Delay': delay,
                'Direction': map(lambda x: x.replace('\n', ' '), map(str.strip, data[0]))
            }
            c -= 1
        for i in r.values():
            if i['Direction'][0]:
                graph.append(["From: %s" % i['Direction'][0], i['Delay']])
            else:
                graph.append(["By: %s" % i['Direction'][1], i['Delay']])
        totalDelay = sum(map(lambda x: x['Delay'], r.values()))
        summary = {
            'From': n.get('from'),
            'To': n.get('to'),
            'Cc': n.get('cc'),
            'Subject': n.get('Subject'),
            'MessageID': n.get('Message-ID'),
            'Date': n.get('Date'),
        }
        return render_template('index.html', data=r, totalDelay=totalDelay, summary=summary, n=n, graph=flask.Markup(graph))
    else:
        return render_template('index.html')


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=8080)
