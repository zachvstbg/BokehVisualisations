from flask import Flask, render_template
from bokeh.embed import components
from math import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.transform import cumsum
'''
    - Showing a pie chart
    - Chart is stand-alone (i.e not dynamic)
'''

# get the Flask app running
app = Flask(__name__)

# make plot
def make_plot():
    # prepare the data
    x = {
        'United States': 157,
        'United Kingdom': 93,
        'Japan': 89,
        'China': 63,
        'Germany': 44,
        'India': 42,
        'Italy': 40,
        'Australia': 35,
        'Brazil': 32,
        'France': 31,
        'Taiwan': 31,
        'Spain': 29
    }

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = Category20c[len(x)]

    p = figure(plot_height=350, title="Pie Chart", toolbar_location=None, x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='country', source=data)

    tooltips = ("@country: @value")
    hover = HoverTool(tooltips=tooltips)
    p.add_tools(hover)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return p




# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Pie chart')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
