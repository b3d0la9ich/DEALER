from flask import Blueprint

bp = Blueprint('employees', __name__, template_folder='../../templates/employees')

from . import routes  # noqa
