from flask import Blueprint

bp = Blueprint('categories', __name__)

from app.categories import routes