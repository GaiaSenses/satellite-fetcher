from flask import Blueprint, render_template

blueprint = Blueprint('', __name__)

@blueprint.get('/')
def get():
    return render_template('index.html')
