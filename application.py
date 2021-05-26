from flask import Flask, render_template, request, jsonify
from plot_graph import *


application = Flask(__name__)

treemapJSON  = draw_treemap()
geo_mapJSON = draw_geo_map()
barJSON = draw_barchart()
case_vaccJSON = case_vacc()


@application.route('/')
def index():
    return render_template('index.html', plot={'treemap': treemapJSON, 'geo_map':geo_mapJSON, 'barchart':barJSON, 'case_vacc':case_vaccJSON})


if __name__ == '__main__':
    application.run()
