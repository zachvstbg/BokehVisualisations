from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.layouts import row
import numpy as np
import holoviews as hv
from holoviews.operation import histogram
from holoviews import opts

# renderer = hv.Store.renderers['bokeh'].instance(mode='server', holomap='server')
# options = hv.Store.options(backend='bokeh')

# hv.extension('bokeh')
renderer = hv.renderer('bokeh')

# this is the app
app = Flask(__name__)

def modify_doc(doc):
    points = hv.Points(np.random.randn(10000, 2))
    points2 = hv.Points(np.random.randn(100, 2) * 2 + 1)
    xhist, yhist = (histogram(points2, bin_range=(-5, 5), dimension=dim) *
                    histogram(points, bin_range=(-5, 5), dimension=dim)
                    for dim in 'xy')

    composition = (points2 * points) << yhist.opts(width=125) << xhist.opts(height=125)
    composition.opts(opts.Histogram(alpha=0.3))

    final = composition

    plot = renderer.get_plot(final)
    layout = row(plot.state)
    # renderer.server_doc(layout)

    doc.add_root(layout)

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
