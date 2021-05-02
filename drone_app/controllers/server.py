# coding=utf-8
"""
Server Módulo
"""
import logging

from flask import render_template, request, jsonify, Response

import config
from models.drone_manager import TelloDrone, BasicPatrolMiddleware

logger = logging.getLogger(__name__)
app = config.app


def get_drone():
    """ Recupera o Drone Manager. """
    return TelloDrone(patrol_middleware=BasicPatrolMiddleware())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/controller/')
def controller():
    return render_template('controller.html')


@app.route('/api/command/', methods=['POST'])
def command():
    cmd = request.form.get('command')
    logger.info({'action': 'command', 'cmd': cmd})
    drone = get_drone()
    if cmd == 'takeOff':
        drone.takeoff()
    if cmd == 'land':
        drone.land()
    if cmd == 'speed':
        speed = request.form.get('speed')
        logger.info({'action': 'command', 'cmd': cmd, 'speed': speed})
        if speed:
            drone.set_speed(int(speed))
    if cmd == 'up':
        drone.up()
    if cmd == 'down':
        drone.down()
    if cmd == 'forward':
        drone.forward()
    if cmd == 'back':
        drone.back()
    if cmd == 'clockwise':
        drone.clockwise()
    if cmd == 'counterClockwise':
        drone.count_clockwise()
    if cmd == 'left':
        drone.left()
    if cmd == 'right':
        drone.right()
    if cmd == 'flipFront':
        drone.flip_forward()
    if cmd == 'flipBack':
        drone.flip_back()
    if cmd == 'flipLeft':
        drone.flip_left()
    if cmd == 'flipRight':
        drone.flip_right()
    if cmd == 'patrol':
        drone.patrol()
    if cmd == 'stopPatrol':
        drone.stop_patrol()

    return jsonify(status='success'), 200


def video_generator():
    drone = get_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            jpeg +
            b'\r\n\r\n'
        )


@app.route('/video/streaming')
def video_feed():
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


def run():
    app.run(host=config.WEB_ADDRESS, port=config.WEB_PORT, threaded=True)
