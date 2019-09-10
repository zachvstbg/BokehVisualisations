from bokeh.plotting import figure
from bokeh.embed import components
from flask import Flask, render_template
from bokeh.models import HoverTool
import numpy as np

'''
    - Showing a hexbin Bokeh chart in Flask app
    - Chart is stand-alone (i.e not dynamic)
    - Hover tool added separately
'''

# get the Flask app running
app = Flask(__name__)


# make plot
def make_plot():
    # prepare the data
    n = 500
    x = 2 + 2 * np.random.standard_normal(n)
    y = 2 + 2 * np.random.standard_normal(n)

    p = figure(title='Hexbin for 500 points', match_aspect=True, tools='pan, wheel_zoom, reset',
               background_fill_color='#440154')
    p.grid.visible = False

    r, bins = p.hexbin(x, y, size=0.5, hover_color='pink', hover_alpha=0.8)
    p.circle(x, y, color='white', size=1)

    tooltips = [('count', '@c'), ('(q,r)', '(@q, @r)')]
    hover = HoverTool(tooltips=tooltips, mode='mouse', point_policy='follow_mouse', renderers=[r])

    p.add_tools(hover)

    return p


# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Hexbin plot')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
