from flask import Flask, render_template
from plot import get_plot
import os

app = Flask(__name__)


@app.get('/')
def single_converter():

    plot = get_plot()
    plot.savefig(os.path.join('../static', 'images', 'plot.png'))

    return render_template('ipc_fcs.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
