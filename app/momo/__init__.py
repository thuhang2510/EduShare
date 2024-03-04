from flask import Blueprint

bp = Blueprint('momo', __name__)

from app.momo import routes