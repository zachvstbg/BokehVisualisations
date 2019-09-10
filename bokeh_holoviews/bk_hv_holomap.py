from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np
import holoviews as hv
from bokeh.layouts import layout

renderer = hv.renderer('bokeh').instance(mode='server')

# this is the app
app = Flask(__name__)


def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

frequencies = [0.5, 0.75, 1.0, 1.25]
curve_dict = {f:sine_curve(0,f) for f in frequencies}
hmap = hv.HoloMap(curve_dict, kdims='frequency')

bk_app = renderer.app(hmap)


@app.route('/', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("bk_hv_embed.html", script=script, template="Flask")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    # need to set the websocket origin to the address - doesnt work with localhost:8000 only
    server = Server({'/': bk_app}, io_loop=IOLoop())
                    # allow_websocket_origin=["127.0.0.1:8000"])
    server.start()
    server.show('/')
    server.io_loop.start()


from threading import Thread

Thread(target=bk_worker).start()

if __name__ == '__main__':
    print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
    print()
    print('Multiple connections may block the Bokeh app in this configuration!')
    print('See "flask_gunicorn_embed.py" for one way to run multi-process')
    app.run(port=8000)
