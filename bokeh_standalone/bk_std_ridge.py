from bokeh.plotting import figure
from bokeh.embed import components
from flask import Flask, render_template
from numpy import linspace
from scipy.stats.kde import gaussian_kde
from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
from bokeh.sampledata.perceptions import probly
import colorcet as cc

'''
    - Showing a ridge plot in Bokeh on a Flask app
    - Chart is stand-alone (i.e not dynamic)
'''

# get the Flask app running
app = Flask(__name__)


# function for ridge
def ridge(category, data, scale=20):
    return list(zip([category] * len(data), scale * data))


# make plot
def make_plot():
    # prepare data stuff - take the keys from the data in order of likelihood
    categories = list(reversed(probly.keys()))
    palette = [cc.rainbow[i * 15] for i in range(17)]
    x = linspace(-20, 110, 500)
    source = ColumnDataSource(data=dict(x=x))

    p = figure(y_range=categories, plot_width=900, x_range=(-5, 105), toolbar_location=None)

    for i, cat in enumerate(reversed(categories)):
        pdf = gaussian_kde(probly[cat])
        y = ridge(cat, pdf(x))
        source.add(y, cat)
        p.patch('x', cat, color=palette[i], alpha=0.6, line_color="black", source=source)

    p.outline_line_color = None
    p.background_fill_color = "#efefef"

    p.xaxis.ticker = FixedTicker(ticks=list(range(0, 101, 10)))
    p.xaxis.formatter = PrintfTickFormatter(format="%d%%")

    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "#dddddd"
    p.xgrid.ticker = p.xaxis[0].ticker

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None

    p.y_range.range_padding = 0.12

    return p


# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Ridge plot')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
