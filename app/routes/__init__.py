from flask import Blueprint

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

from app.routes import main
from app.routes import auth