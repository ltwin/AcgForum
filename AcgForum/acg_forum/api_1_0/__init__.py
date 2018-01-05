from flask import Blueprint

api = Blueprint('api', __name__)

from . import article, passport, register


@api.after_request
def after_request(response):
    if response.headers.get('Content-Type').startswith('text'):
        response.headers['Content-Type'] = 'application/json'
    return response
