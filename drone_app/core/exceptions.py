# coding=utf-8
"""
Módulo para Drone Exceptions.
"""


class DroneManagerNotFound(Exception):
    """ Classe para exceção de Drone Manager não encontrado. """

    def __init__(self):
        super(DroneManagerNotFound, self).__init__(
            'Antes de executar o patrulhamento você deve informar um AbstractDroneManager.')


class DroneSnapShotDirNotFound(Exception):
    """ Classe para exceção de Drone Manager não encontrado. """

    def __init__(self):
        super(DroneSnapShotDirNotFound, self).__init__(
            'O diretório de imagens para snapshots não existe.')
