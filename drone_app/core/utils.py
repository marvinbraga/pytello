# coding=utf-8
"""
Módulo para classes de utilização geral.
"""
import time


class Retry:
    """ Classe para Operacionalizar Tentativas. """

    def __init__(self, check_method, iter_number, wait=0.3):
        self._wait = wait
        self._iter_number = iter_number
        self._check_method = check_method

    def go(self):
        """ Executa as tentativas. """
        result = self.__go_with_method() if type(self._check_method) == 'function' else self.__go_with_attr()
        return result

    def __go_with_method(self):
        retry = 0
        result = False
        while self._check_method():
            time.sleep(self._wait)
            if retry < self._iter_number:
                result = True
                break
            retry += 1
        return result

    def __go_with_attr(self):
        retry = 0
        result = False
        while self._check_method:
            time.sleep(0.3)
            if retry < self._iter_number:
                result = True
                break
            retry += 1
        return result
