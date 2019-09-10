from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.sampledata.iris import flowers
from flask import Flask, render_template
from bokeh.models import HoverTool

# this is the app
app = Flask(__name__)


def modify_doc(doc):
    # prepare stuff for the colors
    colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}
    flowers['color'] = flowers['species'].apply(lambda c: colormap[c])
    source = ColumnDataSource(data=flowers)

    p = figure(title='Iris Morphology', x_axis_label='Petal Length', y_axis_label='Petal Width')
    p.circle(source=source, x='petal_length', y='petal_width', fill_alpha=0.2, size=10, hover_alpha=0.5,
             legend='species', color='color')

    p.legend.location = 'bottom_right'

    tooltips = [('index', '$index'), ('(x,y)', '(@petal_length, @petal_width)'), ('desc', '@species')]
    hover = HoverTool(tooltips=tooltips)

    p.add_tools(hover)

    doc.add_root(p)
    doc.title = "Static on server"


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
