# coding=utf-8
"""
Módulo de conexão com o Tello Drone.
"""
import logging
import sys
import time
from enum import Enum

from abstract_drone import AbstractDroneManager, AbstractPatrolMiddleware

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


# COMMAND_PORT = 8889
# STATE_PORT = 8890
# VIDEO_STREAM_PORT = 11111

class TelloFlipPosition(Enum):
    """ Posições para o drone fazer flip. """
    left = 'i'
    right = 'r'
    forward = 'f'
    back = 'b'


class TelloDrone(AbstractDroneManager):
    """ Classe Específica para o Drone Tello. """
    DEFAULT_DISTANCE = 0.30
    DEFAULT_SPEED = 10
    DEFAULT_DEGREE = 10

    def __init__(self, host_ip='192.168.10.3', host_port=8889, drone_ip='192.168.10.1', drone_port=8889,
                 is_imperial=False, speed=DEFAULT_SPEED, middleware=None):
        super(TelloDrone, self).__init__(host_ip, host_port, drone_ip, drone_port, is_imperial, speed, middleware)

    def _init_commands(self):
        self.send_command('command')
        self.send_command('streamon')
        self.set_speed(self.speed)

    def takeoff(self):
        """ Info """
        self.send_command('takeoff')
        return self

    def land(self):
        """ Voltar para o chão. """
        self.send_command('land')
        return self

    def _move(self, direction, distance):
        """ Método para movimentar o drone em certa direção e distância. """
        distance = float(distance)
        distance = int(round(distance * 30.48)) if self.is_imperial else int(round(distance * 100))
        return self.send_command(f'{direction} {distance}')

    def up(self, distance=DEFAULT_DISTANCE):
        """ Método para subir o drone. """
        self._move('up', distance)
        return self

    def down(self, distance=DEFAULT_DISTANCE):
        """ Método para descer o drone. """
        self._move('down', distance)
        return self

    def left(self, distance=DEFAULT_DISTANCE):
        """ Método para subir o drone. """
        self._move('left', distance)
        return self

    def right(self, distance=DEFAULT_DISTANCE):
        """ Método para subir o drone. """
        self._move('right', distance)
        return self

    def forward(self, distance=DEFAULT_DISTANCE):
        """ Método para subir o drone. """
        self._move('forward', distance)
        return self

    def back(self, distance=DEFAULT_DISTANCE):
        """ Método para subir o drone. """
        self._move('back', distance)
        return self

    def set_speed(self, speed):
        """ Método para ajustar a velocidade do drone. """
        self.send_command(f'speed {speed}')
        return self

    def clockwise(self, degree=DEFAULT_DEGREE):
        """ Girar no sentido horário. """
        self.send_command(f'cw {degree}')
        return self

    def count_clockwise(self, degree=DEFAULT_DEGREE):
        """ Girar no sentido anti-horário. """
        self.send_command(f'ccw {degree}')
        return self

    def _flip(self, position: TelloFlipPosition):
        """ Método para executar o flip. """
        self.send_command(f'flip {position.value}')
        return self

    def flip_left(self):
        """ Executa o flip para a esquerda. """
        self._flip(TelloFlipPosition.left)
        return self

    def flip_right(self):
        """ Executa o flip para a direita. """
        self._flip(TelloFlipPosition.right)
        return self

    def flip_forward(self):
        """ Executa o flip para a frente. """
        self._flip(TelloFlipPosition.forward)
        return self

    def flip_back(self):
        """ Executa o flip para a trás. """
        self._flip(TelloFlipPosition.back)
        return self


class BasicPatrolMiddleware(AbstractPatrolMiddleware):
    """ Faz o patrulhamento básico. """

    def _process(self, status, *args, **kwargs):
        process_id = status
        if process_id == 1:
            self._drone_manager.up()
        elif process_id == 2:
            self._drone_manager.clockwise(90)
        elif process_id == 3:
            self._drone_manager.down()
        elif process_id == 4:
            process_id = 0
        time.sleep(3)
        return process_id


if __name__ == '__main__':
    patrol_middleware = BasicPatrolMiddleware()
    drone_manager = TelloDrone(middleware=patrol_middleware)
    try:
        patrol_middleware.set_drone_manager(drone_manager)
        drone_manager.set_speed(100).takeoff()
        time.sleep(7)
        drone_manager.clockwise(90).clockwise(90).clockwise(90).clockwise(90)
        time.sleep(3)
        drone_manager.count_clockwise(90).count_clockwise(90).count_clockwise(90).count_clockwise(90)
        time.sleep(3)

        drone_manager.forward()
        time.sleep(5)
        drone_manager.right()
        time.sleep(5)
        drone_manager.back()
        time.sleep(5)
        drone_manager.left()
        time.sleep(5)

        drone_manager.set_speed(10)
        time.sleep(1)
        drone_manager.up()
        time.sleep(5)
        drone_manager.down()
        time.sleep(5)

        drone_manager.flip_left()
        time.sleep(3)
        drone_manager.flip_right()
        time.sleep(3)
        drone_manager.flip_forward()
        time.sleep(3)
        drone_manager.flip_back()
        time.sleep(3)

        drone_manager.patrol()
        time.sleep(45)
        drone_manager.stop_patrol()

        drone_manager.land()
    finally:
        drone_manager.stop()
