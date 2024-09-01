from flask import Blueprint

bp = Blueprint('mange', __name__)

from app.mange import routes