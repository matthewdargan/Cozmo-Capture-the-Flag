import multiprocessing
import socket
from sys import platform
from typing import List

import cozmo

from linux_tools import cozmo_interface
from utils.message_forwarder import start_connection, receive_message
from windows_tools import xbox_controller


def cozmo_program(robot: cozmo.robot.Robot):
    """
    Main entry point for running the controller logic in the capture the flag game.

    :param robot: a secondary robot in the game
    """

    # establish connection to the network and message retrieval
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    message: List[str] = []

    xbox_thread: multiprocessing.Process = multiprocessing.Process()

    # setup controller functionality
    if platform.system() == 'Windows':
        xbox_thread = multiprocessing.Process(target=xbox_controller.cozmo_program(robot))
    else:
        xbox_thread = multiprocessing.Process(target=cozmo_interface.cozmo_program(robot))

    xbox_thread.start()

    while 'Exit' not in message:
        message = receive_message(connection)

    # shutdown and exit the game, someone won the game
    xbox_thread.terminate()
    robot.say_text('Game over!')


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
