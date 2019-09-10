from bokeh.plotting import figure
from bokeh.embed import components
from flask import Flask, render_template
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
import numpy as np

'''
    - Showing a colormapped bar chart
    - Chart is stand-alone (i.e not dynamic)
    - Legend separately
'''

# get the Flask app running
app = Flask(__name__)


# make plot
def make_plot():
    # prepare the data
    fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
    counts = [5, 3, 4, 2, 4, 6]

    source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))

    # get the grid
    p = figure(x_range=fruits, plot_height=350, toolbar_location=None, title='Fruit Counts')
    p.vbar(x='fruits', top='counts', width=0.9, source=source, legend='fruits',
           line_color='white', fill_color=factor_cmap('fruits', palette=Spectral6, factors=fruits))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = 9
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    return p


# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Colormap bars')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
