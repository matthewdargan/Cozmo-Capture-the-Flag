import socket
import subprocess
import platform
from typing import List

import cozmo

from common.message_forwarder import start_connection, receive_message
from common.setup import team_colors


def cozmo_program(robot: cozmo.robot.Robot):
    """
    Main entry point for running the controller logic in the capture the flag game.

    :param robot: a secondary robot in the game
    """



    # setup controller functionality
    if platform.system() == 'Windows':
        subprocess.call(['python', 'xbox_controller.py'])
    else:
        subprocess.call(['python', 'cozmo_interface.py'])

    while :
        message = receive_message(connection)




if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
