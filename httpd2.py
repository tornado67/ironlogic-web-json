import os
from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy


MAX_CONTENT_LEN=2000

app = Flask(__name__)


app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/', methods = ['POST'])
def main():
    if request.method != 'POST':
        raise BadRequest('Not implemented', status_code=501)
    answer = []
   
    if int(request.headers.get('Content-Length') or 0) > MAX_CONTENT_LEN:
        raise  BadRequest('Too long', status_code=400)
    try:
        jsn =  request.get_json()
    except ValueError:
        raise  BadRequest('Malformed json', status_code=400)
    sn = jsn.get('sn')
    type = jsn.get('type')


    return 'OK'


if __name__ == '__main__':
    app.run()