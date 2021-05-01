# coding=utf-8
"""
Módulo dos decorators de comandos do drone.
"""
import time

from core.abstract_decorator import AbstractDecorator


class TestClockwiseDecorator(AbstractDecorator):
    """ Classe para testar movimentos de giros. """

    def execute(self, *args, **kwargs):
        """
        Processamento principal.
        :param args:
        :param kwargs:
        :return: self
        """
        self._drone_manager.clockwise(90).clockwise(90).clockwise(90).clockwise(90)
        time.sleep(3)
        self._drone_manager.count_clockwise(90).count_clockwise(90).count_clockwise(90).count_clockwise(90)
        time.sleep(3)
        super().execute(args, kwargs)
        return self


class TestSidesDecorator(AbstractDecorator):
    """ Classe para testar movimentos de lados. """

    def execute(self, *args, **kwargs):
        """
        Processamento principal.
        :param args:
        :param kwargs:
        :return: self
        """
        self._drone_manager.forward()
        time.sleep(5)
        self._drone_manager.right()
        time.sleep(5)
        self._drone_manager.back()
        time.sleep(5)
        self._drone_manager.left()
        time.sleep(5)
        super().execute(args, kwargs)
        return self


class TestUpDownDecorator(AbstractDecorator):
    """ Classe para testar movimentos de lados. """

    def execute(self, *args, **kwargs):
        """
        Processamento principal.
        :param args:
        :param kwargs:
        :return: self
        """
        self._drone_manager.set_speed(10)
        time.sleep(1)
        self._drone_manager.up()
        time.sleep(5)
        self._drone_manager.down()
        time.sleep(5)
        super().execute(args, kwargs)
        return self


class TestFlipDecorator(AbstractDecorator):
    """ Classe para testar movimentos de lados. """

    def execute(self, *args, **kwargs):
        """
        Processamento principal.
        :param args:
        :param kwargs:
        :return: self
        """
        self._drone_manager.flip_left()
        time.sleep(3)
        self._drone_manager.flip_right()
        time.sleep(3)
        self._drone_manager.flip_forward()
        time.sleep(3)
        self._drone_manager.flip_back()
        time.sleep(3)
        super().execute(args, kwargs)
        return self


class TestPatrolDecorator(AbstractDecorator):
    """ Classe para testar movimentos de lados. """

    def execute(self, *args, **kwargs):
        """
        Processamento principal.
        :param args:
        :param kwargs:
        :return: self
        """
        self._drone_manager.patrol()
        time.sleep(45)
        self._drone_manager.stop_patrol()
        super().execute(args, kwargs)
        return self
