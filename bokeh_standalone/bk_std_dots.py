from bokeh.plotting import figure
from bokeh.sampledata.iris import flowers
from bokeh.embed import components
from flask import Flask, render_template
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource

'''
    - Showing a circle-glyph (multiple-series) Bokeh chart in Flask app
    - Chart is stand-alone (i.e not dynamic)
    - Legend, hover added separately
'''

# get the Flask app running
app = Flask(__name__)


# make plot
def make_plot():
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

    return p


# the app route
@app.route('/')
def index():
    plot = make_plot()

    # embed in the HTML
    script, div = components(plot)

    # render the template
    return render_template('std_basic.html', script=script, div=div, type='Simple dot plot (circles)')


if __name__ == '__main__':
    app.run(port=8080, debug=True)
