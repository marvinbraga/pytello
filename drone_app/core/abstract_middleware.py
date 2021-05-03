# coding=utf-8
"""
Módulo de Middleware Básico.
"""
import os.path
from abc import ABCMeta, abstractmethod

import cv2 as cv

from config import PROJECT_ROOT


class BaseMiddleware(metaclass=ABCMeta):
    """ Classe base para middleware. """
    def __init__(self, next_middleware=None):
        self._next = next_middleware

    @staticmethod
    def get_cascade(file_name):
        """
        Carrega o cascade do arquivo XML do opencv.
        :param file_name: nome do cascade
        :return: obj
        """
        file = os.path.normpath(os.path.join(PROJECT_ROOT, f'data/{file_name}'))
        if not os.path.isfile(file):
            raise FileNotFoundError()
        return cv.CascadeClassifier(file)

    @abstractmethod
    def _process(self, frame):
        pass

    def process(self, frame):
        """
        Método para processamento do middleware.
        :param frame:
        :return:
        """
        result = self._process(frame)
        if self._next:
            result = self._next.process(result)

        return result
