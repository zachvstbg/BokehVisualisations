from bokeh.plotting import figure
from bokeh.embed import components
from flask import Flask, render_template
import numpy as np
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.sampledata.stocks import AAPL
'''
    - Showing a range tool chart
    - Chart is stand-alone (i.e not dynamic)
'''

# get the Flask app running
app = Flask(__name__)

# make plot
def make_plot():
    # prepare the data
    dates = np.array(AAPL['date'], dtype=np.datetime64)
    source = ColumnDataSource(data=dict(date=dates, close=AAPL['adj_close']))

    # prepare the chart
    p = figure(plot_height=300, plot_width=800, tools='xpan', toolbar_location=None,
               x_axis_type='datetime', x_axis_location='above',
               background_fill_color="#efefef", x_range=(dates[1500], dates[2500]))

    p.line('date', 'close', source=source)
    p.yaxis.axis_label = 'Price'

    # get the selection/dragger
    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    plot_height=130, plot_width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="", toolbar_location=None, background_fill_color="#efefef")

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    select.line('date', 'close', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool

    return column(p, select)


# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Range tool')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
