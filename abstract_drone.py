# coding=utf-8
"""
Módulo para Drone Abstrato.
"""
import contextlib
import logging
import socket
import sys
import threading
import time
from abc import ABCMeta, abstractmethod
from threading import Event, Thread

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


class DroneManagerNotFound(Exception):
    """ Classe para exceção de Drone Manager não encontrado. """

    def __init__(self):
        super(DroneManagerNotFound, self).__init__(
            'Antes de executar o patrulhamento você deve informar um AbstractDroneManager.')


class AbstractPatrolMiddleware(metaclass=ABCMeta):
    """ Classe abstrata para implementações de regras de patrulhamento """

    def __init__(self, next_middleware=None):
        self._drone_manager = None
        self._next_middleware = next_middleware

    def add_next(self, value):
        """ Adicional middleware """
        self._next_middleware = value
        return self

    def remove_next(self):
        """ Remove o middleware. """
        self._next_middleware = None
        return self

    @abstractmethod
    def _process(self, status, *args, **kwargs):
        """
        Método que contem o processo de patrulhamento e deve ser implementado em cada uma de
        suas especializações.
        :return: Inteiro referente ao valor do status. Utilize 0 para reiniciar o processo,
        caso necessário.
        """
        pass

    def process(self, status, *args, **kwargs):
        """ Método para executar processamento de patrulhamento """
        if not self._drone_manager:
            raise DroneManagerNotFound()

        process_id = self._process(status, args, kwargs)
        if self._next_middleware:
            process_id = self._next_middleware.process(status, args, kwargs)
        return process_id

    def set_drone_manager(self, value):
        """ Informa o gerenciador do drone para todos os middlewares vinculados. """
        self._drone_manager = value
        if self._next_middleware:
            self._next_middleware.set_drone_manager(value)
        return self


class AbstractDroneManager(metaclass=ABCMeta):
    """ Classe para gerenciamento do drone. """

    logger = logging.getLogger('AbstractDroneManager')

    def __init__(self, host_ip, host_port, drone_ip, drone_port, is_imperial, speed, middleware):
        self.middleware = middleware
        self.speed = speed
        self.is_imperial = is_imperial
        self.drone_ip = drone_ip
        self.drone_port = drone_port
        self.drone_address = (drone_ip, drone_port)
        self.host_ip = host_ip
        self.host_port = host_port
        # Conexão
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host_ip, self.host_port))
        self.response = None
        # Patrol
        self.patrol_event = None
        self.is_patrol = False
        self._patrol_semaphore = threading.Semaphore()
        self._thread_patrol = None
        # Stop
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

    def receive_response(self, stop_event):
        """ Info """
        while not stop_event.is_set():
            try:
                self.response, ip = self.socket.recvfrom(3000)
                self.logger.info({'action': 'receive_response', 'response': self.response})
            except socket.error as e:
                self.logger.error({'action': 'receive_response', 'error': e})
                break

    def stop(self):
        """ Fecha a conexão """
        self.stop_event.set()
        self._retry(self._response_thread.is_alive, 30)
        self.socket.close()

    def send_command(self, command):
        """ Registrar o envio de um comando. """
        self.logger.info({'action': 'send_command', 'command': command})
        self.socket.sendto(command.encode('utf-8'), self.drone_address)

        self._retry(self._is_none_response, 3)

        response = None
        if not self._is_none_response():
            response = self.response.decode('utf-8')

        self.response = None
        return response

    def patrol(self):
        """ Inicializa as condições para fazer o patrulhamento. """
        if not self.is_patrol:
            self.patrol_event = Event()
            self._thread_patrol = Thread(
                target=self._patrol,
                args=(self._patrol_semaphore, self.patrol_event, self.middleware, self.logger, )
            )
            self.is_patrol = True
            self._thread_patrol.start()
        return self

    def stop_patrol(self):
        """ Método para parar o patrulhamento. """
        if self.is_patrol:
            try:
                self.patrol_event.set()
                self._retry(self._thread_patrol.is_alive, 300)
            finally:
                self.is_patrol = False
        return self

    @staticmethod
    def _patrol(semaphore, stop_event, middleware, logger):
        """ Método para executar o patrulhamento. """
        is_acquire = semaphore.acquire(blocking=False)
        if is_acquire:
            logger.info({'action': '_patrol', 'status': 'acquire'})
            with contextlib.ExitStack() as stack:
                stack.callback(semaphore.release)
                status = 0
                while not stop_event.is_set():
                    status += 1
                    if middleware:
                        status = middleware.process(status)
        else:
            logger.warning({'action': '_patrol', 'status': 'not_acquire'})
