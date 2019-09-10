from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure
from os.path import dirname, join
import pandas as pd

# this is the app
app = Flask(__name__)

# this is the data - sourcing from folders
DATA_DIR = join(dirname(__file__), 'data\\daily')
DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

# supporting methods for getting the data - load ticker from the csv files
def nix(val, lst):
    return [x for x in lst if x != val]

def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})

# combine the data - 2 tickers
def get_data(t1, t2):
    df1 = load_ticker(t1)
    df2 = load_ticker(t2)
    data = pd.concat([df1, df2], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    data['t1_returns'] = data[t1+'_returns']
    data['t2_returns'] = data[t2+'_returns']
    return data

def modify_doc(doc):
    # set up the widgets
    stats = PreText(text='', width=500)
    ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS))
    ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS))

    # set the plots
    source = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
    source_static = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
    tools = 'pan,wheel_zoom,xbox_select,reset'

    corr = figure(plot_width=350, plot_height=350,
                  tools='pan,wheel_zoom,box_select,reset')
    corr.circle('t1_returns', 't2_returns', size=2, source=source,
                selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

    ts1 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
    ts1.line('date', 't1', source=source_static)
    ts1.circle('date', 't1', size=1, source=source, color=None, selection_color="orange")

    ts2 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
    ts2.x_range = ts1.x_range
    ts2.line('date', 't2', source=source_static)
    ts2.circle('date', 't2', size=1, source=source, color=None, selection_color="orange")

    # call backs
    def ticker1_change(attrname, old, new):
        ticker2.options = nix(new, DEFAULT_TICKERS)
        update()

    def ticker2_change(attrname, old, new):
        ticker1.options = nix(new, DEFAULT_TICKERS)
        update()

    def update(selected=None):
        t1, t2 = ticker1.value, ticker2.value

        data = get_data(t1, t2)
        source.data = source.from_df(data[['t1', 't2', 't1_returns', 't2_returns']])
        source_static.data = source.data

        update_stats(data, t1, t2)

        corr.title.text = '%s returns vs. %s returns' % (t1, t2)
        ts1.title.text, ts2.title.text = t1, t2

    def update_stats(data, t1, t2):
        stats.text = str(data[[t1, t2, t1 + '_returns', t2 + '_returns']].describe())

    ticker1.on_change('value', ticker1_change)
    ticker2.on_change('value', ticker2_change)

    def selection_change(attrname, old, new):
        t1, t2 = ticker1.value, ticker2.value
        data = get_data(t1, t2)
        selected = source.selected.indices
        if selected:
            data = data.iloc[selected, :]
        update_stats(data, t1, t2)

    source.selected.on_change('indices', selection_change)

    # set up layout
    widgets = column(ticker1, ticker2, stats)
    main_row = row(corr, widgets)
    series = column(ts1, ts2)
    layout = column(main_row, series)

    # initialize
    update()

    doc.add_root(layout)
    doc.title = "Stocks"


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
