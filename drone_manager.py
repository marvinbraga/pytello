# coding=utf-8
"""
Módulo de conexão com o Tello Drone.
"""
import logging
import socket
import sys
import time
from abc import ABCMeta, abstractmethod
from threading import Thread, Event

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


# COMMAND_PORT = 8889
# STATE_PORT = 8890
# VIDEO_STREAM_PORT = 11111


class BaseDroneManager(metaclass=ABCMeta):
    """ Classe para gerenciamento do drone. """

    def __init__(self, host_ip, host_port, drone_ip, drone_port):
        self.drone_port = drone_port
        self.drone_ip = drone_ip
        self.host_port = host_port
        self.host_ip = host_ip
        self.drone_address = (drone_ip, drone_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host_ip, self.host_port))
        self.response = None
        self.stop_event = Event()
        self._response_thread = Thread(target=self.receive_response, args=(self.stop_event,))
        self._response_thread.start()
        self._init_commands()

    @abstractmethod
    def _init_commands(self):
        pass

    def __del__(self):
        self.stop()

    def _retry(self, check_method, iter_number):
        """ Método para fazer tentativas em uma checagem.  """
        retry = 0
        while check_method():
            time.sleep(0.3)
            if retry > iter_number:
                break
            retry += 1
        return self

    def _is_none_response(self):
        """ Verifica se existe uma response. """
        return self.response is None

    def stop(self):
        """ Fecha a conexão """
        self.stop_event.set()
        self._retry(self._response_thread.is_alive, 30)
        self.socket.close()

    def receive_response(self, stop_event):
        """ Info """
        while not stop_event.is_set():
            try:
                self.response, ip = self.socket.recvfrom(3000)
                logger.info({'action': 'receive_response', 'response': self.response})
            except socket.error as e:
                logger.error({'action': 'receive_response', 'error': e})
                break

    def send_command(self, command):
        """ Registrar o envio de um comando. """
        logger.info({'action': 'send_command', 'command': command})
        self.socket.sendto(command.encode('utf-8'), self.drone_address)

        self._retry(self._is_none_response, 3)

        response = None
        if not self._is_none_response():
            self.response.decode('utf-8')

        self.response = None
        return response


class TelloDrone(BaseDroneManager):
    """ Classe Específica para o Drone Tello. """

    def __init__(self, host_ip='192.168.10.2', host_port=8889, drone_ip='192.168.10.1', drone_port=8889):
        super(TelloDrone, self).__init__(host_ip, host_port, drone_ip, drone_port)

    def _init_commands(self):
        self.send_command('command')
        self.send_command('streamon')

    def takeoff(self):
        """ Info """
        self.send_command('takeoff')

    def land(self):
        """ Voltar para o chão. """
        self.send_command('land')


if __name__ == '__main__':
    drone_manager = TelloDrone()
    try:
        drone_manager.takeoff()
        time.sleep(5)
        drone_manager.land()
    finally:
        drone_manager.stop()
