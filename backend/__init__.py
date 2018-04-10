# package init file
from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from backend.apis import index
from backend.apis import broker
from backend.apis import client
from backend.apis import dashboard
from backend.apis import settings
from backend.apis import topic
