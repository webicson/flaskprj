from flask import Blueprint

bp = Blueprint('vendors', __name__)

from app.vendors import routes