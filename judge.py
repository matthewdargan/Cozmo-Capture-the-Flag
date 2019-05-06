"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""
import concurrent.futures
import socket
from typing import Dict

from common.message_forwarder import start_connection, receive_message
from common.setup import *


def cozmo_program(robot: cozmo.robot.Robot):
    """
    Main entry point for running the scoring logic in the capture the flag game.

    :param robot: judge robot in the game
    """

    # get number of teams playing in the game
    while True:
        try:
            teams: int = int(input("How many teams are playing?"))
        except ValueError:
            print("Invalid input type")
            continue
        if teams < 2:
            print("Must be between 2 and 3")
            continue
        elif teams > 3:
            print("Must be between 1 and 3")
            continue
        else:
            break

    # get the id of the team the judge is on
    while True:
        try:
            team_id: int = int(input("Which team is this judge on?"))
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

    # get the corresponding team colors and opponent colors
    team_colors, opponent_colors = get_team_colors(teams)

    # set backpack color and head angle
    robot.set_all_backpack_lights(team_colors[team_id])
    robot.set_head_angle(cozmo.util.Angle(degrees=20))

    # establish connection to the network and message retrieval
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    message: List[str] = []

    # setup the game
    robot_cubes: List[LightCube] = setup(robot, opponent_colors[team_id])

    # set default score
    robot_score: int = 0

    # continuously check the cube object held up to the judge and increment the score accordingly
    while 'Exit' not in message:
        captured_cube = None

        # wait for one the cubes to be shown to the judge
        try:
            captured_cube = robot.world.wait_for_observed_light_cube(timeout=0.5)
        except concurrent.futures._base.TimeoutError:
            pass

        # increment score and change cube color if the cube was valid and in-play
        if captured_cube in robot_cubes:
            captured_cube.set_lights(team_colors[team_id])
            robot_cubes.remove(captured_cube)
            robot_score += 1

        # break out of the loop if the maximum score has been reached, cube wait doesn't let the loop terminate
        if robot_score == 3:
            break

        message = receive_message(connection)

    # print the win state and terminate based on scoring the maximum number of points or receiving the exit message
    if robot_score == 3:
        connection.send(b'Exit %d' % team_id)
        print('You won!')
    else:
        print('Robot %s won!' % message[1])


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
