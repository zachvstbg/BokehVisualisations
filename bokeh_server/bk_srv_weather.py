from flask import Flask, render_template
from os.path import join, dirname
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.models import BoxSelectTool, LassoSelectTool
from bokeh.plotting import figure, curdoc
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np
from bokeh.layouts import row, column
import datetime
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.palettes import Blues4

# this is the app
app = Flask(__name__)

# this is the data
STATISTICS = ['record_min_temp', 'actual_min_temp', 'average_min_temp', 'average_max_temp', 'actual_max_temp',
              'record_max_temp']


def get_dataset(src, name, distribution):
    df = src[src.airport == name].copy()
    del df['airport']
    df['date'] = pd.to_datetime(df.date)
    # timedelta here instead of pd.DateOffset to avoid pandas bug < 0.18 (Pandas issue #11925)
    df['left'] = df.date - datetime.timedelta(days=0.5)
    df['right'] = df.date + datetime.timedelta(days=0.5)
    df = df.set_index(['date'])
    df.sort_index(inplace=True)
    if distribution == 'Smoothed':
        window, order = 51, 3
        for key in STATISTICS:
            df[key] = savgol_filter(df[key], window, order)

    return ColumnDataSource(data=df)


def make_plot(source, title):
    plot = figure(x_axis_type="datetime", plot_width=800, tools="", toolbar_location=None)
    plot.title.text = title

    plot.quad(top='record_max_temp', bottom='record_min_temp', left='left', right='right',
              color=Blues4[2], source=source, legend="Record")
    plot.quad(top='average_max_temp', bottom='average_min_temp', left='left', right='right',
              color=Blues4[1], source=source, legend="Average")
    plot.quad(top='actual_max_temp', bottom='actual_min_temp', left='left', right='right',
              color=Blues4[0], alpha=0.5, line_color="black", source=source, legend="Actual")

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Temperature (F)"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.grid.grid_line_alpha = 0.3

    return plot


def modify_doc(doc):
    # make the plot selection stuff
    city = 'Austin'
    distribution = 'Discrete'

    cities = {
        'Austin': {
            'airport': 'AUS',
            'title': 'Austin, TX',
        },
        'Boston': {
            'airport': 'BOS',
            'title': 'Boston, MA',
        },
        'Seattle': {
            'airport': 'SEA',
            'title': 'Seattle, WA',
        }
    }

    city_select = Select(value=city, title='City', options=sorted(cities.keys()))
    distribution_select = Select(value=distribution, title='Distribution', options=['Discrete', 'Smoothed'])

    df = pd.read_csv(join(dirname(__file__), 'data\\2015_weather.csv'))
    source = get_dataset(df, cities[city]['airport'], distribution)
    plot = make_plot(source, "Weather data for " + cities[city]['title'])

    def update_plot(attrname, old, new):
        city = city_select.value
        plot.title.text = "Weather data for " + cities[city]['title']

        src = get_dataset(df, cities[city]['airport'], distribution_select.value)
        source.data.update(src.data)

    city_select.on_change('value', update_plot)
    distribution_select.on_change('value', update_plot)
    controls = column(city_select, distribution_select)

    doc.add_root(row(plot, controls))
    doc.title = "Selection Histogram"


@app.route('/', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("bk_hv_embed.html", script=script, template="Flask")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    # need to set the websocket origin to the address - doesnt work with localhost:8000 only
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(),
                    allow_websocket_origin=["127.0.0.1:8000"])
    server.start()
    server.io_loop.start()


from threading import Thread

Thread(target=bk_worker).start()

if __name__ == '__main__':
    print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
    print()
    print('Multiple connections may block the Bokeh app in this configuration!')
    print('See "flask_gunicorn_embed.py" for one way to run multi-process')
    app.run(port=8000)
