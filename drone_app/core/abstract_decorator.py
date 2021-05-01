# coding=utf-8
"""
Módulo para Decorator Abstrato
"""
from abc import ABCMeta


class AbstractDecorator(metaclass=ABCMeta):
    """ Classe abstrata para decorator. """

    def __init__(self, drone_manager, decorator=None):
        self._drone_manager = drone_manager
        self._decorator = decorator

    def execute(self, *args, **kwargs):
        """
        Método para executar processamento central
        :param args:
        :param kwargs:
        :return: self
        """
        if self._decorator:
            self._decorator.execute(args, kwargs)
        return self
