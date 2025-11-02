from flask import Blueprint


bp = Blueprint('cars', __name__, template_folder='../../templates/cars')


from . import routes
