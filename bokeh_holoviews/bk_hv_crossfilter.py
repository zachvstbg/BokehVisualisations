from flask import Flask, render_template
from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
import numpy as np
import holoviews as hv
from bokeh.layouts import layout
from bokeh.models import Slider, Button
from bokeh.layouts import row, widgetbox
from bokeh.models import Select
from bokeh.plotting import curdoc
from bokeh.sampledata.autompg import autompg


# this is the app
app = Flask(__name__)

# load the data
df = autompg.copy()
SIZES = list(range(6,22,3))
ORIGINS = ['North America', 'Europe', 'Asia']

# data cleanup
df.cyl = [str(x) for x in df.cyl]
df.origin = [ORIGINS[x-1] for x in df.origin]
df['year'] = [str(x) for x in df.yr]
del df['yr']
df['mfr'] = [x.split()[0] for x in df.name]
df.loc[df.mfr=='chevy', 'mfr'] = 'chevrolet'
df.loc[df.mfr=='chevroelt', 'mfr'] = 'chevrolet'
df.loc[df.mfr=='maxda', 'mfr'] = 'mazda'
df.loc[df.mfr=='mercedes-benz', 'mfr'] = 'mercedes'
df.loc[df.mfr=='toyouta', 'mfr'] = 'toyota'
df.loc[df.mfr=='vokswagen', 'mfr'] = 'volkswagen'
df.loc[df.mfr=='vw', 'mfr'] = 'volkswagen'
del df['name']

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype==object]
continuous = [x for x in columns if x not in discrete]
quantileable = [x for x in continuous if len(df[x].unique())>20]

# create the renderers
renderer = hv.renderer('bokeh').instance(mode='server')

def modify_doc(doc):
    options = hv.Store.options(backend='bokeh')
    options.Points = hv.Options('plot', width=800, height=600, size_index=None,)
    options.Points = hv.Options('style', cmap='rainbow', line_color='black')

    def create_figure():
        label = "%s vs %s" % (x.value.title(), y.value.title())
        kdims = [x.value, y.value]
        opts, style = {}, {}
        opts['color_index'] = color.value if color.value != 'None' else None
        if size.value != 'None':
            opts['size_index'] = size.value
            opts['scaling_factor'] = (1. / df[size.value].max()) * 200
        points = hv.Points(df, kdims=kdims, label=label).opts(plot=opts, style=style)
        return renderer.get_plot(points).state

    def update(attr, old, new):
        layout.children[1] = create_figure()

    x = Select(title='X-Axis', value='mpg', options=quantileable)
    x.on_change('value', update)

    y = Select(title='Y-Axis', value='hp', options=quantileable)
    y.on_change('value', update)

    size = Select(title='Size', value='None', options=['None'] + quantileable)
    size.on_change('value', update)

    color = Select(title='Color', value='None', options=['None'] + quantileable)
    color.on_change('value', update)

    controls = widgetbox([x, y, color, size], width=200)
    layout = row(controls, create_figure())

    doc.add_root(layout)
    return doc

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
