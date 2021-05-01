# coding=utf-8
"""
Módulo de Testes de Movimentação do Drone.
"""
import time

from decorators import TestClockwiseDecorator, TestSidesDecorator, TestUpDownDecorator, TestFlipDecorator, \
    TestPatrolDecorator
from drone_app.models.drone_manager import TelloDrone, BasicPatrolMiddleware


def test_drone_manager():
    """ Executar Testes. """
    drone_manager = TelloDrone(patrol_middleware=BasicPatrolMiddleware())
    try:
        drone_manager.set_speed(100).takeoff()
        time.sleep(7)

        TestClockwiseDecorator(
            drone_manager, TestSidesDecorator(
                drone_manager, TestUpDownDecorator(
                    drone_manager, TestFlipDecorator(
                        drone_manager, TestPatrolDecorator(
                            drone_manager
                        )
                    )
                )
            )
        ).execute()

        drone_manager.land()
    finally:
        drone_manager.stop()
