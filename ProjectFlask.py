from flask import Flask
from flask import render_template
import os


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rapporten')
def rapporten():
    return render_template('rapporten.html')

@app.route('/instellingen')
def instellingen():
    return render_template('instellingen.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=True)
