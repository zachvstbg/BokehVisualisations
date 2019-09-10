from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.models import BoxSelectTool, LassoSelectTool
from bokeh.plotting import figure, curdoc
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np
from bokeh.layouts import gridplot

# this is the app
app = Flask(__name__)

# this is the data

# create some data - normal population samples
x1 = np.random.normal(loc=5.0, size=400) * 100
y1 = np.random.normal(loc=10.0, size=400) * 10
x2 = np.random.normal(loc=5.0, size=800) * 50
y2 = np.random.normal(loc=10.0, size=800) * 10
x3 = np.random.normal(loc=55.0, size=200) * 10
y3 = np.random.normal(loc=4.0, size=200) * 10

# this is the combined data
x = np.concatenate((x1, x2, x3))
y = np.concatenate((y1, y2, y3))


def modify_doc(doc):
    # set the tools and basic figure (i.e. scatter plot)
    tools = 'pan, wheel_zoom, box_select, lasso_select, reset'
    p = figure(tools=tools, plot_width=600, plot_height=600, min_border=10, min_border_left=50,
               toolbar_location='above', x_axis_location=None, y_axis_location=None,
               title='Linked Histograms')
    p.background_fill_color = '#fafafa'
    p.select(BoxSelectTool).select_every_mousemove = False
    p.select(LassoSelectTool).select_every_mousemove = False

    r = p.scatter(x, y, size=3, color='#3A5785', alpha=0.5)

    # create the horizontal histogram
    hhist, hedges = np.histogram(x, bins=20)
    hzeros = np.zeros(len(hedges) - 1)
    hmax = max(hhist) * 1.1

    LINE_ARGS = dict(color="#3A5785", line_color=None)

    ph = figure(toolbar_location=None, plot_width=p.plot_width, plot_height=200, x_range=p.x_range,
                y_range=(-hmax, hmax), min_border=10, min_border_left=50, y_axis_location="right")
    ph.xgrid.grid_line_color = None
    ph.yaxis.major_label_orientation = np.pi / 4
    ph.background_fill_color = "#fafafa"

    ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hhist, color="white", line_color="#3A5785")
    hh1 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.5, **LINE_ARGS)
    hh2 = ph.quad(bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros, alpha=0.1, **LINE_ARGS)

    # create the vertical histogram
    vhist, vedges = np.histogram(y, bins=20)
    vzeros = np.zeros(len(vedges) - 1)
    vmax = max(vhist) * 1.1

    pv = figure(toolbar_location=None, plot_width=200, plot_height=p.plot_height, x_range=(-vmax, vmax),
                y_range=p.y_range, min_border=10, y_axis_location="right")
    pv.ygrid.grid_line_color = None
    pv.xaxis.major_label_orientation = np.pi / 4
    pv.background_fill_color = "#fafafa"

    pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist, color="white", line_color="#3A5785")
    vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
    vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

    layout = gridplot([[p, pv], [ph, None]], merge_tools=False)

    # curdoc().add_root(layout)
    # curdoc().title = "Selection Histogram"

    doc.add_root(layout)
    doc.title = "Selection Histogram"

    def update(attr, old, new):
        inds = new
        if len(inds) == 0 or len(inds) == len(x):
            hhist1, hhist2 = hzeros, hzeros
            vhist1, vhist2 = vzeros, vzeros
        else:
            neg_inds = np.ones_like(x, dtype=np.bool)
            neg_inds[inds] = False
            hhist1, _ = np.histogram(x[inds], bins=hedges)
            vhist1, _ = np.histogram(y[inds], bins=vedges)
            hhist2, _ = np.histogram(x[neg_inds], bins=hedges)
            vhist2, _ = np.histogram(y[neg_inds], bins=vedges)

        hh1.data_source.data["top"] = hhist1
        hh2.data_source.data["top"] = -hhist2
        vh1.data_source.data["right"] = vhist1
        vh2.data_source.data["right"] = -vhist2

    r.data_source.selected.on_change('indices', update)


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
