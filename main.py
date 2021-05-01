# coding=utf-8
"""
Main Module
"""
import logging
import sys

import config
import drone_app.controllers.server


def get_log_stream(is_log_in_file=False):
    """ Recupera o ambiente do log. """
    stream = sys.stdout
    if is_log_in_file:
        stream = config.LOG_FILE
    return stream


logging.basicConfig(level=logging.INFO, stream=get_log_stream())

if __name__ == '__main__':
    drone_app.controllers.server.run()
