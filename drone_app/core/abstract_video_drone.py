# coding=utf-8
"""
Módulo Base para Drone com Vídeo
"""
import os
import socket
import subprocess
import time
from abc import ABCMeta, abstractmethod
from threading import Thread

import cv2
import numpy as np

from core.abstract_drone import AbstractDroneManager


class AbstractVideoSetup(metaclass=ABCMeta):
    """ Classe para configurações de vídeo """

    def __init__(self, default_distance=0.30, default_speed=10, default_degree=10, frame_x=960, frame_y=720, divider=3):
        self._divider = divider
        self._frame_y = int(frame_y / self._divider)
        self._frame_x = int(frame_x / self._divider)
        self._default_degree = default_degree
        self._default_speed = default_speed
        self._default_distance = default_distance
        self._frame_area = self._frame_x * self._frame_y
        self._frame_size = int(self._frame_area * 3)
        self._frame_center_x = self._frame_x / 2
        self._frame_center_y = self._frame_y / 2
        self._command = None

    @property
    def divider(self):
        """ Expõe o valor de _divider. """
        return self._divider

    @property
    def frame_size(self):
        """ Expõe o valor de _frame_size. """
        return self._frame_size

    @property
    def frame_y(self):
        """ Expõe o valor de _frame_y. """
        return self._frame_y

    @property
    def frame_x(self):
        """ Expõe o valor de _frame_x. """
        return self._frame_x

    @property
    def frame_area(self):
        """ Expõe o valor de _frame_area. """
        return self._frame_area

    @property
    def frame_center_x(self):
        """ Expõe o valor de _frame_center_x. """
        return self._frame_center_x

    @property
    def frame_center_y(self):
        """ Expõe o valor de _frame_center_y. """
        return self._frame_center_y

    @abstractmethod
    def _command_mount(self):
        pass

    @property
    def command(self):
        """ Recupera o comando com o streamer de vídeo. """
        self._command_mount()
        return self._command


class VideoSetupFFmpeg(AbstractVideoSetup):
    """ Classe para configurar o streamer de FFmpeg. """

    def _command_mount(self):
        self._command = f'c:\\ffmpeg\\bin\\ffmpeg.exe -hwaccel auto -hwaccel_device opencl -i pipe:0 ' \
                        f'-pix_fmt bgr24 -s {self._frame_x}x{self._frame_y} -f rawvideo pipe:1'
        return self


class AbstractDroneVideoManager(AbstractDroneManager):
    """ Classe para gerenciar drones com vídeo """

    def __init__(self, host_ip, host_port, drone_ip, drone_port, is_imperial, speed, patrol_middleware, video_setup,
                 face_detect_middleware):
        super(AbstractDroneVideoManager, self).__init__(host_ip, host_port, drone_ip, drone_port, is_imperial, speed,
                                                        patrol_middleware)
        self.video_setup = video_setup
        cmd = self.video_setup.command.split(' ')
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.proc_std_in = self.proc.stdin
        self.proc_std_out = self.proc.stdout
        self.video_port = 11111
        # Thread
        self._receive_video_thread = Thread(
            target=self.receive_video,
            args=(self.stop_event, self.proc_std_in, self.host_ip, self.video_port,)
        )
        self._receive_video_thread.start()
        # Face Detect
        self._is_enable_face_detect = False
        self._face_detect_middleware = face_detect_middleware

    def enable_face_detect(self):
        """ Ativa a detecção de faces """
        self._is_enable_face_detect = True
        return self

    def disable_face_detect(self):
        """ Desativa a detecção de faces """
        self._is_enable_face_detect = False
        return self

    def stop(self):
        """ Parar a conexão com o drone. """
        super(AbstractDroneVideoManager, self).stop()
        # Para o vídeo
        # os.kill(self.proc.pid, 9)
        # Windows
        import signal
        os.kill(self.proc.pid, signal.CTRL_C_EVENT)

    def receive_video(self, stop_event, pipe_in, host_ip, video_port):
        """
        Método para receber vídeo.
        :param stop_event:
        :param pipe_in:
        :param host_ip:
        :param video_port:
        :return:
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_video:
            sock_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock_video.settimeout(.5)
            sock_video.bind((host_ip, video_port))
            data = bytearray(2048)
            while not stop_event.is_set():
                try:
                    size, address = sock_video.recvfrom_into(data)
                    self.logger.info({'action': 'receive_video', 'data': data})
                except socket.timeout as ex:
                    self.logger.warning({'action': 'receive_video', 'ex': ex})
                    time.sleep(0.5)
                    continue
                except socket.error as ex:
                    self.logger.error({'action': 'receive_video', 'ex': ex})
                    break

                try:
                    pipe_in.write(data[:size])
                    pipe_in.flush()
                except Exception as ex:
                    self.logger.error({'action': 'receive_video', 'ex': ex})
                    break

    def video_binary_generator(self):
        """ Gerador de vídeo """

        while True:
            try:
                frame = self.proc_std_out.read(self.video_setup.frame_size)
            except Exception as ex:
                self.logger.error({'action': 'video_binary_generator', 'ex': ex})
                continue

            if not frame:
                continue

            frame = np.fromstring(frame, np.uint8).reshape(self.video_setup.frame_y, self.video_setup.frame_x,
                                                           self.video_setup.divider)
            yield frame

    def video_jpeg_generator(self):
        """ Gerador de vídeo Jpeg. """
        for frame in self.video_binary_generator():
            if self._is_enable_face_detect:
                if self.is_patrol:
                    self.stop_patrol()
                # Aplica a detecção de faces
                frame = self._face_detect_middleware.process(frame)

            _, jpeg = cv2.imencode('.jpg', frame)
            jpeg_binary = jpeg.tobytes()
            yield jpeg_binary
