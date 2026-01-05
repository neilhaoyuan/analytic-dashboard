from flask import Flask
from flask_caching import Cache

server = Flask(__name__)

cache = Cache(server, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 900
})