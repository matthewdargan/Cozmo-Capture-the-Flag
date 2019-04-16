"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

import multiprocessing
import platform
import socket
import time
from typing import List, Tuple

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id, LightCube

from linux_tools import cozmo_interface
from message_forwarder import start_connection, receive_message
from windows_tools import xbox_controller


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light):
    """
    Main entry point for running the logic for the capture the flag game.

    TODO: abstract this out so its a list of up to 4 robots
    :param robot: main robot in the game
    :param cube_color color for this team's cubes
    """

    # get the number of cubes the users want to play with in the game
    while True:
        try:
            num_cubes: int = int(input("How many cubes do you want to play with?"))
        except ValueError:
            print("Invalid input type")
            continue
        if num_cubes < 0:
            print("Input must be positive")
            continue
        elif num_cubes > 3:
            print("Invalid Number of Cubes")
            continue
        else:
            break

    # get the value for the maximum score in the game from the users
    while True:
        try:
            max_score: int = int(input("How many points do you want to play up to?"))
        except ValueError:
            print("Invalid input type")
            continue
        if max_score < 0:
            print("Input must be positive")
            continue
        else:
            break

    # send the start message to the network
    connection = start_connection("10.0.1.10", 5000)
    connection.send(b'Start')

    # setup the game
    connection, robot_cubes, robot_origin = setup(robot, num_cubes, cube_color)

    # reformat robot 1's origin
    robot_origin: Tuple[float, float] = (robot_origin.position.x, robot_origin.position.y)

    # get robot 2's origin
    origin_message = receive_message(connection)
    robot2_origin = (float(origin_message[0][1]), float(origin_message[0][2]))

    # set default scores for each side
    robot1_score: int = 0
    robot2_score: int = 0

    # previous lists of the cube statuses for each of the robots
    robot1_prev_statuses: List[bool] = [False for _ in range(num_cubes)]
    robot2_prev_statuses: List[bool] = [False for _ in range(num_cubes)]

    # continuously check the location of the cubes to see if the opponent has captured one of them
    while robot1_score or robot2_score is not max_score:
        # receive the other player's cube locations and use is_in_base to compare positions for scoring purposes
        messages = receive_message(connection)

        # unpack robot 2's coordinates from the network message
        robot2_x_coordinates: List[float] = [float(coord) for i, coord in enumerate(messages[1:]) if i % 2 is not 0]
        robot2_y_coordinates: List[float] = [float(coord) for i, coord in enumerate(messages[1:]) if i % 2 is 0]
        robot2_coordinates: List[Tuple[float, float]] = list(zip(robot2_x_coordinates, robot2_y_coordinates))

        # unpack robot 1's coordinates to check them against robot 2's origin
        robot1_coordinates = []
        for cube in range(len(robot_cubes)):
            cube_position: cozmo.util.Position = robot_cubes[cube].pose.Position
            robot1_coordinates.append((cube_position.x, cube_position.y))

        # get the current statuses for whether a new cube of the opponent is in the user's base
        robot1_acquire_statuses: List[bool] = is_in_base(robot2_coordinates, robot_origin)
        robot2_acquire_statuses: List[bool] = is_in_base(robot1_coordinates, robot2_origin)

        # if a user has acquired one of the opponent's cubes then increment their score
        for difference in check_status_differences(robot1_prev_statuses, robot1_acquire_statuses):
            if difference == 1 or difference == -1:
                robot1_score += 1
                print("Robot 1 scored!")

                # update previous lists
                robot1_prev_statuses = robot1_acquire_statuses

        for difference in check_status_differences(robot2_prev_statuses, robot2_acquire_statuses):
            if difference == 1 or difference == -1:
                robot2_score += 1
                print("Robot 2 scored!")

                # update previous lists
                robot2_prev_statuses = robot2_acquire_statuses

        # if all of the cubes have already been found, let the users reset the locations and then resume playing
        if robot1_score % num_cubes == 0:
            # send the reset message over the network to the slave computer so it knows to reset robot 2's coordinates
            connection.send(b'Reset')
            time.sleep(0.5)

        if robot2_score % num_cubes == 0:
            reset(robot_cubes, robot)


def setup(robot: cozmo.robot.Robot, num_cubes: int, cube_color: cozmo.lights.Light) -> (socket.socket,
                                                                                        List[LightCube],
                                                                                        cozmo.util.Pose):
    """
    Setup up the cozmo program to run for each computer to use.

    :param robot robot to get cubes for
    :param num_cubes number of cubes we are playing with
    :param cube_color color of this team's cubes
    """

    # set up network connection to send cube positions over between computers
    connection = start_connection("10.0.1.10", 5000)

    # lists for storing robot1's and robot2's cubes
    robot_cubes: List[LightCube] = []

    # add the cubes to their respective lists
    for cube_num in range(num_cubes):
        if cube_num == 1:
            robot_cubes.append(robot.world.get_light_cube(LightCube1Id))
        elif cube_num == 2:
            robot_cubes.append(robot.world.get_light_cube(LightCube2Id))
        else:
            robot_cubes.append(robot.world.get_light_cube(LightCube3Id))

    # set the colors for robot1's cubes to blue and robot2's to red
    for cube in range(len(robot_cubes)):
        robot_cubes[cube].set_lights(cube_color)

    start_message = receive_message(connection)

    while start_message[0][0] is not 'Start':
        start_message = receive_message(connection)

    # start the game once the master computer sends out the start message over the network
    print("Set Cozmo's in position to play.")

    # give a 10 second period for the users to set their robots in their bases and hide their cubes
    time.sleep(10)

    # get robot1's and robot2's origins
    robot_origin: cozmo.util.Pose = robot.pose

    print("Start playing!")

    # allow the users to start controlling the robots here
    if platform.system() == 'Windows':
        multiprocessing.Process(target=xbox_controller.cozmo_program(robot)).start()
    else:
        multiprocessing.Process(target=cozmo_interface.cozmo_program(robot)).start()

    return connection, robot_cubes, robot_origin


def is_in_base(robot_coordinates: List[Tuple[float, float]], base_boundaries: Tuple[float, float]) -> List[bool]:
    """
    Check the location of the cubes relative to an opponent's base.

    :param robot_coordinates coordinates for a robot's cubes
    :param base_boundaries the boundaries for a robot's base to see if someone scored
    :return: a list of booleans corresponding to the cube acquirement statuses for a robot
    """
    robot_cond: List[bool] = [False for _ in range(len(robot_coordinates))]

    for i, coordinate in enumerate(robot_coordinates):
        if 0 <= coordinate[0] <= base_boundaries[0] + 300 and 0 <= coordinate[1] <= base_boundaries[1] + 300:
            robot_cond[i] = True

    return robot_cond


def check_status_differences(list1: List[bool], list2: List[bool]) -> List[int]:
    """
    Check the differences between two boolean lists that contain the current statuses of cube positions
    relative to an opponent's base.

    :param list1: first cube status list
    :param list2: second cube status list
    :return: a list of integers containing either 1s or -1s which represent differences or 0s which means no change
    """
    results: List[int] = []

    for i in range(len(list1)):
        results.append(list1[i] - list2[i])

    return results


def reset(robot_cubes: List[LightCube], robot: cozmo.robot.Robot):
    """
    Reset the game state so that we allow the user to re-hide their cubes and them continue playing.

    :param robot_cubes: list of the robot's cubes that need to be reset
    :param robot: one of the current robots in the game
    """

    # TODO: have the robots themselves reset the cubes, add error handling to make sure the cubes are not still
    #       in an opponent's base in case they do not reset the locations of the cubes in time

    # timeout the game for 15 seconds so the users have time to re-hide their cubes
    time.sleep(15)

    # reset the positions of all of the cubes for a robot
    for i, _ in enumerate(robot_cubes):
        if i == 0:
            robot_cubes[i] = robot.world.get_light_cube(LightCube1Id)
        elif i == 1:
            robot_cubes[i] = robot.world.get_light_cube(LightCube2Id)
        else:
            robot_cubes[i] = robot.world.get_light_cube(LightCube3Id)


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
