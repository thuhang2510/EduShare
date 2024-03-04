from flask import Blueprint

bp = Blueprint('momo', __name__)

from app.auth import routes