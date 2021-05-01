# coding=utf-8
"""
Módulo de conexão com o Tello Drone.
"""
import time
from enum import Enum

from drone_app.core.abstract_drone import AbstractDroneManager, AbstractPatrolMiddleware


# COMMAND_PORT = 8889
# STATE_PORT = 8890
# VIDEO_STREAM_PORT = 11111

class TelloFlipPosition(Enum):
    """ Posições para o drone fazer flip. """
    left = 'l'
    right = 'r'
    forward = 'f'
    back = 'b'


class TelloDrone(AbstractDroneManager):
    """ Classe Específica para o Drone Tello. """
    DEFAULT_DISTANCE = 0.30
    DEFAULT_SPEED = 10
    DEFAULT_DEGREE = 10

    def __init__(self, host_ip='192.168.10.3', host_port=8889, drone_ip='192.168.10.1', drone_port=8889,
                 is_imperial=False, speed=DEFAULT_SPEED, patrol_middleware=None):
        super(TelloDrone, self).__init__(host_ip, host_port, drone_ip, drone_port,
                                         is_imperial, speed, patrol_middleware)
        self.patrol_middleware.set_drone_manager(self)

    def _init_commands(self):
        """ Comandos de Inicialização do Drone. """
        self.send_command('command')
        self.send_command('streamon')
        self.set_speed(self.speed)

    def takeoff(self):
        """ Levantar Voo. """
        self.send_command('takeoff')
        return self

    def land(self):
        """ Voltar para o chão. """
        self.send_command('land')
        return self

    def emergency(self):
        """ Parar os motores imediatamente. """
        self.send_command('emergency')
        return self

    def go(self, x, y, z, speed=DEFAULT_SPEED):
        """ Para para a posição determinada com a velocidade informada. """
        self.send_command(f'go {x} {y} {z} {speed}')
        return self

    def go_mid(self, x, y, z, mid, speed=DEFAULT_SPEED):
        """ Para para a posição determinada com a velocidade informada. """
        self.send_command(f'go {x} {y} {z} {speed} {mid}')
        return self

    def stop(self):
        """ Para o drone no ar. (Funciona a qualquer momento). """
        self.send_command('stop')
        return self

    def curve(self, x1, y1, z1, x2, y2, z2, speed=DEFAULT_SPEED):
        """ Faz uma curva de acordo com as coordenadas. """
        self.send_command(f'curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}')
        return self

    def curve_mid(self, x1, y1, z1, x2, y2, z2, mid, speed=DEFAULT_SPEED):
        """
        Voe em uma curva de acordo com as duas coordenadas fornecidas da missão
        Pad ID em 'velocidade' (cm / s). Se o raio do arco não estiver na faixa
        de 0,5 a 10 metros, ele responderá com um erro.
        """
        self.send_command(f'curve {x1} {y1} {z1} {x2} {y2} {z2} {speed} {mid}')
        return self

    def set_wifi_pw(self, ssid, password):
        """
        Atualiza os parâmetros de acesso wi-fi.
        :param ssid: Nome da rede.
        :param password: Senha da rede.
        :return: self.
        """
        self.send_command(f'wifi {ssid} {password}')

    def set_station_mode(self, ssid, password):
        """
        Set the Tello to station mode, and connect to a new access point with the access
        point's ssid and password.
        :param ssid: Updated wi-fi name.
        :param password: Update wi-fi password.
        :return: self
        """
        self.send_command(f'ap {ssid} {password}')

    def jump(self, x, y, z, mid1, mid2, speed=DEFAULT_SPEED):
        """
        Voe para as coordenadas x, y e z da missão Pad ID1 e reconheça as
        coordenadas 0, 0, z da missão pad ID2 e gire para o valor de guinada.
        """
        self.send_command(f'jump {x} {y} {z} {speed} yaw {mid1} {mid2}')
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

    def get_speed(self):
        """
        Obtem a velocidade corrente.
        :return: Int
        """
        return int(self.send_command('speed?'))

    def get_battery(self):
        """
        Obtem o percentual de carga da bateria.
        :return: Int
        """
        return int(self.send_command('battery?'))

    def get_time(self):
        """
        Obtem o tempo de vôo.
        :return: string
        """
        return self.send_command('time?')

    def get_wifi_snr(self):
        """
        Obtem o SNR da rede Wi-fi.
        :return: string
        """
        return self.send_command('wifi?')

    def get_sdk(self):
        """
        Obtem a versão do SDK Tello.
        :return: string
        """
        return self.send_command('sdk?')

    def get_sn(self):
        """
        Obtem o número do serial Tello.
        :return: string
        """
        return self.send_command('sn?')


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
        elif process_id > 3:
            process_id = 0
        time.sleep(3)
        return process_id
