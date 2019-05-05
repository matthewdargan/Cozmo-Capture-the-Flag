import socket
import subprocess
from sys import platform
from typing import List

import cozmo

from common.message_forwarder import start_connection, receive_message
from common.setup import team_colors


def cozmo_program(robot: cozmo.robot.Robot):
    """
    Main entry point for running the controller logic in the capture the flag game.

    :param robot: a secondary robot in the game
    """

    # get the id of the team the judge is on
    while True:
        try:
            team_id: int = int(input("Which team is this player on?"))
        except ValueError:
            print("Invalid input type")
            continue
        if team_id < 1:
            print("Must be between 1 and 2")
            continue
        elif team_id > 3:
            print("Must be between 1 and 2")
            continue
        else:
            break

    # set backpack color
    robot.set_all_backpack_lights(team_colors[team_id])

    # establish connection to the network and message retrieval
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    message: List[str] = []

    # setup controller functionality
    if platform.system() == 'Windows':
        subprocess.call(['python', 'windows_tools/xbox_controller.py'])
    else:
        subprocess.call(['python', 'linux_tools/cozmo_interface.py'])

    while 'Exit' not in message:
        message = receive_message(connection)

    if int(message[1]) == team_id:
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabCelebrate).wait_for_completed()
    else:
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabUnhappy).wait_for_completed()


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
