from flask import Blueprint, current_app, make_response, session
from flask_wtf import csrf

html = Blueprint('html', __name__)


@html.route('/<regex(".*"):file_name>')
def html_file(file_name):
    if not file_name:
        file_name = 'html/index.html'
    elif file_name != 'favicon.ico':
        file_name = 'html/' + file_name + '.html'

    csrf_token = csrf.generate_csrf()
    html_str = current_app.send_static_file(file_name)
    print(html_str)
    response = make_response(html_str)

    response.set_cookie('csrf_token', csrf_token)

    return response
