from flask import Blueprint

daily = Blueprint('daily', __name__)
monthly = Blueprint('monthly', __name__)
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)
settings = Blueprint('settings', __name__)


from app.routes import daily
from app.routes import monthly
from app.routes import auth
from app.routes import main
from app.routes import settings