from flask import render_template, Blueprint, request, g, Response
from peewee import *

app_library = Blueprint('app_library', __name__)

@app_library.route('/')
def index():
    return render_template('index.html')
    
@app_library.route('/search')
def search():
    return render_template('search.html')
