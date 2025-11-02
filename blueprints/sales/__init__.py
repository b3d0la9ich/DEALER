from flask import Blueprint

bp = Blueprint('sales', __name__, template_folder='../../templates/sales')

from . import routes  # noqa
