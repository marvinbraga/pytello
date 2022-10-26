# coding=utf-8
"""
Server Módulo
"""
import logging

from flask import render_template, request, jsonify, Response

import config
from drone_app.models.drone_manager import TelloDrone, BasicPatrolMiddleware, StreamTelloDrone

logger = logging.getLogger(__name__)
app = config.app


def get_drone(video=False):
    """ Recupera o Drone Manager. """
    if video:
        return StreamTelloDrone(patrol_middleware=BasicPatrolMiddleware())
    return TelloDrone(patrol_middleware=BasicPatrolMiddleware())


@app.route('/')
def index():
    """ View para o index. """
    return render_template('index.html')


@app.route('/controller/')
def controller():
    """ View para retornar a página de controles do Drone. """
    return render_template('controller.html')


@app.route('/api/command/', methods=['POST'])
def command():
    """ View para executar comando do Drone. """
    cmd = request.form.get('command')
    logger.info({'action': 'command', 'cmd': cmd})
    drone = get_drone(video=True)
    drone_command = {
        'takeOff': drone.takeoff,
        'land': drone.land,
        'up': drone.up,
        'down': drone.down,
        'forward': drone.forward,
        'back': drone.back,
        'clockwise': drone.clockwise,
        'counterClockwise': drone.count_clockwise,
        'left': drone.left,
        'right': drone.right,
        'flipFront': drone.flip_forward,
        'flipBack': drone.flip_back,
        'flipLeft': drone.flip_left,
        'flipRight': drone.flip_right,
        'patrol': drone.patrol,
        'stopPatrol': drone.stop_patrol,
        'faceDetectAndTrack': drone.enable_face_detect,
        'stopFaceDetectAndTrack': drone.disable_face_detect,
    }.get(cmd)
    if cmd == 'speed':
        speed = request.form.get('speed')
        logger.info({'action': 'command', 'cmd': cmd, 'speed': speed})
        if speed:
            drone.set_speed(int(speed))
    elif cmd == 'snapshot':
        if not drone.snapshot():
            return jsonify(status='fail'), 400
    else:
        if drone_command:
            drone_command()

    return jsonify(status='success'), 200


def video_generator():
    """ Método para disponibilizar imagens recuperadas pelo Drone. """
    drone = get_drone(video=True)
    for jpeg in drone.video_jpeg_generator():
        yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                jpeg +
                b'\r\n\r\n'
        )


@app.route('/video/streaming')
def video_feed():
    """ View para retornar a imagem recuperada do Drone.  """
    try:
        result = video_generator()
        return Response(result, mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logging.error({'action': 'video_streaming', 'exception': str(e)})
        return Response('', mimetype='text/plain')


def run():
    """ Método para inicializar as aplicação. """
    app.run(host=config.WEB_ADDRESS, port=config.WEB_PORT, threaded=True)
