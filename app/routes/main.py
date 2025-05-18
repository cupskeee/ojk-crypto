from flask import render_template
from app.routes import main
from app.utils.decorator import login_required

@main.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

