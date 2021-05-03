# coding=utf-8
"""
Módulo de configuração
"""
import os
from flask import Flask

WEB_ADDRESS = 'localhost'
WEB_PORT = 5000
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(PROJECT_ROOT, 'drone_app/templates')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'drone_app/static')
SNAPSHOT_IMAGE_FOLDER = os.path.join(STATIC_FOLDER, 'img/snapshots')
DEBUG = True
LOG_FILE = 'pytello.log'

app = Flask(__name__, template_folder=TEMPLATES, static_folder=STATIC_FOLDER)
app.debug = DEBUG
