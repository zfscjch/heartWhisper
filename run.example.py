# -*- encoding: utf-8 -*-
# Please use this file in a production deployment.
from gevent import pywsgi
from paper_server import app

CERT_FILE = 'path/to/your/cert/file'
KEY_FILE = 'path/to/your/key/file'

server = pywsgi.WSGIServer(
    ('0.0.0.0', 5000),
    app,
    keyfile=KEY_FILE,
    certfile=CERT_FILE
)

print("Gevent WSGI server starting up on https://0.0.0.0:5000 ...")

server.serve_forever()
