from flask import Blueprint

bp = Blueprint('inq', __name__)

from . import routes  # noqa
