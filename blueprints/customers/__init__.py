from flask import Blueprint


bp = Blueprint('customers', __name__, template_folder='../../templates/customers')


from . import routes
