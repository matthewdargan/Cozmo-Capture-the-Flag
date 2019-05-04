import multiprocessing
import socket
from sys import platform
from typing import List

import cozmo

from linux_tools import cozmo_interface
from common.message_forwarder import start_connection, receive_message
from windows_tools import xbox_controller


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light = cozmo.lights.blue_light):
    """
    Main entry point for running the controller logic in the capture the flag game.

    :param robot: a secondary robot in the game
    :param cube_color color for this team
    """

    # set backpack color
    robot.set_all_backpack_lights(cube_color)

    # get the id of the team the judge is on
    while True:
        try:
            team_id: int = int(input("Which team is this player on?"))
        except ValueError:
            print("Invalid input type")
            continue
        if team_id < 1:
            print("Must be between 1 and 3")
            continue
        elif team_id > 3:
            print("Must be between 1 and 3")
            continue
        else:
            break

    # establish connection to the network and message retrieval
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    message: List[str] = []

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

    if int(message[1]) == team_id:
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabCelebrate).wait_for_completed()
    else:
        robot.play_anim_trigger(cozmo.anim.Triggers.CodeLabUnhappy).wait_for_completed()


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
