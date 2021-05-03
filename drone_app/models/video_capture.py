# coding=utf-8
"""
Módulo de OpenCvVideoCapture.
"""
import os
import time

import cv2
import cv2 as cv

from config import SNAPSHOT_IMAGE_FOLDER
from core.abstract_drone import DroneSnapShotDirNotFound
from core.abstract_middleware import BaseMiddleware
from core.utils import Retry


class OpenCvVideoCapture:
    """ Classe para trabalhar com o OpenCvVideoCapture. """

    def __init__(self, middleware, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._middleware = middleware
        self._cap = cv.VideoCapture(0)

    def execute(self):
        """
        Método para executa o OpenCvVideoCapture
        :return:
        """
        while True:
            ret, img = self._cap.read()
            self._middleware.process(img)

            cv.imshow('frame', img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()


class FaceEyesDetectMiddleware(BaseMiddleware):
    """ Classe middleware para encontrar olhos e face """

    def __init__(self, next_middleware=None):
        super(FaceEyesDetectMiddleware, self).__init__(next_middleware)
        self._face_cascade = self.get_cascade('haarcascade_frontalface_default.xml')
        self._eye_cascade = self.get_cascade('haarcascade_eye.xml')

    def _process(self, frame):
        """
        Encontrar face e olhos.
        :param frame:
        :return:
        """
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
        # print('Faces: ', len(faces))

        for (x, y, w, h) in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            eye_gray = gray[y: y + h, x: x + w]
            eye_color = frame[y: y + h, x: x + w]
            eyes = self._eye_cascade.detectMultiScale(eye_gray)
            # print('Olhos: ', len(eyes))
            for (ex, ey, ew, eh) in eyes:
                cv.rectangle(eye_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                break
            break

        return frame


class FaceDetectMiddleware(BaseMiddleware):
    """ Classe middleware para encontrar olhos e face """

    def __init__(self, next_middleware=None):
        super(FaceDetectMiddleware, self).__init__(next_middleware)
        self._face_cascade = self.get_cascade('haarcascade_frontalface_default.xml')

    def _process(self, frame):
        """
        Encontrar face e olhos.
        :param frame:
        :return:
        """
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            break

        return frame


class DroneFaceDetectMiddleware(BaseMiddleware):
    """ Classe middleware para encontrar olhos e face """

    def __init__(self, next_middleware=None, drone_manager=None):
        super(DroneFaceDetectMiddleware, self).__init__(next_middleware)
        self._drone_manager = drone_manager
        self._face_cascade = self.get_cascade('haarcascade_frontalface_default.xml')

    def _process(self, frame):
        """
        Encontrar face e olhos.
        :param frame:
        :return:
        """
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if self._drone_manager:
                face_center_x = x + (w / 2)
                face_center_y = y + (h / 2)
                diff_x = self._drone_manager.video_setup.frame_center_x - face_center_x
                diff_y = self._drone_manager.video_setup.frame_center_y - face_center_y
                face_area = w * h
                percent_face = face_area / self._drone_manager.video_setup.frame_area
                self.execute_drone_rules(diff_x, diff_y, percent_face)
            break

        return frame

    def execute_drone_rules(self, diff_x, diff_y, percent_face):
        """ Executa as Regras relacionadas à movimentação do drone. """
        drone_x, drone_y, drone_z, speed = 0, 0, 0, self._drone_manager.speed
        if diff_x < -30:
            drone_y = -30
        if diff_x > 30:
            drone_y = 30
        if diff_y < -15:
            drone_z = -30
        if diff_y > 15:
            drone_z = 30
        if percent_face > 0.3:
            drone_x = -30
        if percent_face < -0.02:
            drone_x = 30
        # Movimenta o drone.
        self._drone_manager.go(drone_x, drone_y, drone_z, speed, blocking=False)
        return self


class DroneSnapshotMiddleware(BaseMiddleware):
    """ Classe para processamento de snapshot no drone. """
    
    def __init__(self, next_middleware=None, drone_manager=None):
        super(DroneSnapshotMiddleware, self).__init__(next_middleware)
        self._drone_manager = drone_manager
        if not os.path.exists(SNAPSHOT_IMAGE_FOLDER):
            raise DroneSnapShotDirNotFound()
        self._is_snapshot = False

    def _process(self, frame):
        if self._is_snapshot:
            _, jpeg = cv2.imencode('.jpg', frame)
            jpeg_binary = jpeg.tobytes()

            backup_file = f'{time.strftime("%Y%m%d-%H%M%S")}.jpg'
            file = 'snapshot.jpg'
            for file_name in (backup_file, file):
                file_path = os.path.join(SNAPSHOT_IMAGE_FOLDER, file_name)
                with open(file_path, 'wb') as f:
                    f.write(jpeg_binary)
            self._is_snapshot = False

        return frame

    def snapshot(self):
        """ Aciona o snapshot. """
        self._is_snapshot = True
        return Retry(self._is_snapshot, 3, 0.1).go()


if __name__ == '__main__':
    OpenCvVideoCapture(middleware=FaceEyesDetectMiddleware()).execute()
