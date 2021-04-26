# coding=utf-8
"""
Módulo de OpenCv.
"""
import os.path
from abc import ABCMeta, abstractmethod

import cv2 as cv


class OpenCv:
    """ Classe para trabalhar com o OpenCv. """
    def __init__(self, middleware, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._middleware = middleware
        self._cap = cv.VideoCapture(0)

    def execute(self):
        """
        Método para executa o OpenCv
        :return:
        """
        while True:
            ret, img = self._cap.read()
            self._middleware.process(img)

            cv.imshow('frame', img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()


class BaseMiddleware(metaclass=ABCMeta):
    """ Classe base para middleware. """
    def __init__(self, next_middleware=None):
        self._next = next_middleware

    @staticmethod
    def get_cascade(file_name):
        """
        Carrega o cascade do arquivo XML do opencv.
        :param file_name: nome do cascade
        :return: obj
        """
        file = os.path.normpath(f'./data/{file_name}')
        if not os.path.isfile(file):
            raise FileNotFoundError()
        return cv.CascadeClassifier(file)

    @abstractmethod
    def _process(self, frame):
        pass

    def process(self, frame):
        """
        Método para processamento do middleware.
        :param frame:
        :return:
        """
        self._process(frame)
        if self._next:
            self._next.process(frame)

        return self


class FaceEyesMiddleware(BaseMiddleware):
    """ Classe middleware para encontrar olhos e face """
    def __init__(self, next_middleware=None):
        super(FaceEyesMiddleware, self).__init__(next_middleware)
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
        print('Faces: ', len(faces))

        for (x, y, w, h) in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            eye_gray = gray[y: y + h, x: x + w]
            eye_color = frame[y: y + h, x: x + w]
            eyes = self._eye_cascade.detectMultiScale(eye_gray)
            print('Olhos: ', len(eyes))
            for (ex, ey, ew, eh) in eyes:
                cv.rectangle(eye_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

        return self


if __name__ == '__main__':
    OpenCv(middleware=FaceEyesMiddleware()).execute()
