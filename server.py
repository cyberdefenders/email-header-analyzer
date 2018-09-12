from flask import Flask
from flask import render_template
from flask import request

from email import parser
import time
import dateutil.parser

from datetime import datetime
import re

import pygal
from pygal.style import Style

from IPy import IP
import geoip2.database

import argparse

app = Flask(__name__)
reader = geoip2.database.Reader(
    '%s/data/GeoLite2-Country.mmdb' % app.static_folder)


@app.context_processor
def utility_processor():
    def getCountryForIP(line):
        ipv4_address = re.compile(r"""
            \b((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.
            (?:25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d))\b""", re.X)
        ip = ipv4_address.findall(line)
        if ip:
            ip = ip[0]  # take the 1st ip and ignore the rest
            if IP(ip).iptype() == 'PUBLIC':
                r = reader.country(ip).country
                if r:
                    return {
                        'iso_code': r.iso_code.lower(),
                        'country_name': r.name
                    }
    return dict(country=getCountryForIP)


@app.context_processor
def utility_processor():
    def duration(seconds, _maxweeks=99999999999):
        return ', '.join(
            '%d %s' % (num, unit)
            for num, unit in zip([
                (seconds // d) % m
                for d, m in (
                    (604800, _maxweeks),
                    (86400, 7), (3600, 24),
                    (60, 60), (1, 60))
            ], ['wk', 'd', 'hr', 'min', 'sec'])
            if num
        )
    return dict(duration=duration)


def dateParser(line):
    try:
        r = dateutil.parser.parse(line, fuzzy=True)

    # if the fuzzy parser failed to parse the line due to
    # incorrect timezone information issue #5 GitHub
    except ValueError:
        r = re.findall('^(.*?)\s*\(', line)
        if r:
            r = dateutil.parser.parse(r[0])
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['headers'].strip()
        r = {}
        # Removed data.encode('ascii', 'ignore') because it seems to not required
        n = parser.Parser().parsestr(data.encode('ascii','ignore'))
        graph = []
        received = n.get_all('Received')
        if received:
            received = [i for i in received if ('from' in i or 'by' in i)]
        c = len(received)
        for i in range(len(received)):
            if ';' in received[i]:
                line = received[i].split(';')
            else:
                line = received[i].split('\r\n')
            line = map(str.strip, line)
            line = list(map(lambda x: x.replace('\r\n', ''), line))
            try:
                if ';' in received[i + 1]:
                    next_line = received[i + 1].split(';')
                else:
                    next_line = received[i + 1].split('\r\n')
                next_line = list(map(str.strip, next_line))
                next_line = list(map((lambda x: x.replace('\r\n', '')), next_line))
            except IndexError:
                next_line = None

            org_time = dateParser(line[1])
            if not next_line:
                next_time = org_time
            else:
                next_time = dateParser(next_line[1])

            if line[0].startswith('from'):
                data = re.findall(
                    """
                    from\s+
                    (.*?)\s+
                    by(.*?)
                    (?:
                        (?:with|via)
                        (.*?)
                        (?:id|$)
                        |id|$
                    )""", line[0], re.DOTALL | re.X)
            else:
                data = re.findall(
                    """
                    ()by
                    (.*?)
                    (?:
                        (?:with|via)
                        (.*?)
                        (?:id|$)
                        |id
                    )""", line[0], re.DOTALL | re.X)

            delay = org_time.second - next_time.second
            if delay < 0:
                delay = 0

            try:
                ftime = org_time.strftime('%m/%d/%Y %I:%M:%S %p')
                r[c] = {
                    'Timestmp': org_time,
                    'Time': ftime,
                    'Delay': delay,
                    'Direction': list(map(
                        lambda x: x.replace('\n', ' '),
                        map(str.strip, data[0]))
                    )
                }
                c -= 1
            except IndexError:
                pass

        for i in r.values():
            if i['Direction'][0]:
                graph.append(["From: %s" % i['Direction'][0], i['Delay']])
            else:
                graph.append(["By: %s" % i['Direction'][1], i['Delay']])

        totalDelay = sum(map(lambda x: x['Delay'], r.values()))
        fTotalDelay = utility_processor()['duration'](totalDelay)
        delayed = True if totalDelay else False

        custom_style = Style(
            background='transparent',
            plot_background='transparent',
            font_family='googlefont:Open Sans',
            title_font_size=12,
        )
        line_chart = pygal.HorizontalBar(
            style=custom_style, height=250, legend_at_bottom=True,
            tooltip_border_radius=10)
        line_chart.tooltip_fancy_mode = False
        line_chart.title = 'Total Delay is: %s' % fTotalDelay
        line_chart.x_title = 'Delay in seconds.'
        for i in graph:
            line_chart.add(i[0], i[1])
        chart = line_chart.render(is_unicode=True)

        summary = {
            'From': n.get('from'),
            'To': n.get('to'),
            'Cc': n.get('cc'),
            'Subject': n.get('Subject'),
            'MessageID': n.get('Message-ID'),
            'Date': n.get('Date'),
        }
        return render_template(
            'index.html', data=r, delayed=delayed, summary=summary,
            n=n, chart=chart)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    paramparser = argparse.ArgumentParser(description="Mail Header Analyser")
    paramparser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="Enable debug mode")
    paramparser.add_argument("-b", "--bind", default="127.0.0.1", type=str)
    paramparser.add_argument("-p", "--port", default="8080", type=int)
    args = paramparser.parse_args()

    app.debug = args.debug
    app.run(host=args.bind, port=args.port)
