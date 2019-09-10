from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.layouts import row
import numpy as np
import holoviews as hv

# renderer = hv.Store.renderers['bokeh'].instance(mode='server', holomap='server')
# options = hv.Store.options(backend='bokeh')

# hv.extension('bokeh')
renderer = hv.renderer('bokeh')

# this is the app
app = Flask(__name__)

def modify_doc(doc):
    def sine_curve(phase, freq):
        xvals = [0.1 * i for i in range(100)]
        return hv.Curve((xvals, [np.sin(phase + freq * x) for x in xvals]))

    phases = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
    frequencies = [0.5, 0.75, 1.0, 1.25]

    curve_dict_2D = {(p, f): sine_curve(p, f) for p in phases for f in frequencies}
    gridspace = hv.GridSpace(curve_dict_2D, kdims=['phase', 'frequency'])
    hv.output(size=50)
    hmap = hv.HoloMap(gridspace)

    final = hmap + hv.GridSpace(hmap)

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
