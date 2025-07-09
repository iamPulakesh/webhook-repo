from flask import Blueprint

# create a blueprint named webhook
webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

from . import routes  # This imports routes and attaches them to the blueprint
