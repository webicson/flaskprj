from flask import Blueprint

bp = Blueprint('dids', __name__)

from app.dids import routes