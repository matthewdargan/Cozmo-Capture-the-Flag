"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""
import socket
from typing import List

import cozmo
from cozmo.objects import LightCube

from utils.setup import setup
from utils.message_forwarder import start_connection, receive_message


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light = cozmo.lights.blue_light):
    """
    Main entry point for running the logic for the capture the flag game.

    :param robot: main robot in the game
    :param cube_color color for this team's cubes
    """

    # establish connection to the network and message retrieval
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    message: List[str] = []

    # setup the game
    robot_cubes: List[LightCube] = setup(robot, cube_color)

    # set default score
    robot_score: int = 0

    # continuously check the cube object held up to the judge and increment the score accordingly
    while robot_score is not 3 or 'Exit' not in message:
        # wait for one the cubes to be shown to the judge
        captured_cube: LightCube = robot.world.wait_for_observed_light_cube()

        # increment score and change cube color if the cube was valid and in-play
        if captured_cube in robot_cubes:
            captured_cube.set_lights(cozmo.lights.red_light)
            robot_cubes.remove(captured_cube)
            robot_score += 1

        message = receive_message(connection)

    # print the win state and terminate based on scoring the maximum number of points or receiving the exit message
    if robot_score == 3:
        connection.send(b'Exit')
        print('Robot 1 won!')
    else:
        print('Robot 2 won!')


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
