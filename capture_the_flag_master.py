"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""
import socket
import time
from typing import List, Tuple

import cozmo

from capture_the_flag_functionality import setup, reset
from message_forwarder import start_connection, receive_message


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light = cozmo.lights.blue_light):
    """
    Main entry point for running the logic for the capture the flag game.

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

    # send the start message to the network and the number of cubes the slave computers should use
    connection: socket.socket = start_connection("10.0.1.10", 5000)
    connection.send(b'%d' % num_cubes)

    # set robot 1's origin by estimating the distance between robot 1 and robot 2
    while True:
        try:
            robot_distance: int = int(input("What is the distance between robot 1 and robot 2?\n"
                                            "(Set the robots to be parallel)"))
        except ValueError:
            print("Invalid input type")
            continue
        if robot_distance < 0:
            print("Input must be positive")
            continue
        else:
            break

    robot_origin: cozmo.util.Pose = robot.pose.define_pose_relative_this(cozmo.util.Pose(x=robot_distance, y=0, z=0))
    robot_origin: Tuple[float, float] = (robot_origin.position.x, robot_origin.position.y)

    # setup the game
    robot_cubes, _ = setup(robot, num_cubes, cube_color)

    # get robot 2's origin
    origin_message: List[str] = receive_message(connection)
    robot2_origin: Tuple[float, float] = (float(origin_message[0]), float(origin_message[1]))

    # set default scores for each side
    robot1_score: int = 0
    robot2_score: int = 0

    # previous lists of the cube statuses for each of the robots
    robot1_prev_statuses: List[bool] = [False for _ in range(num_cubes)]
    robot2_prev_statuses: List[bool] = [False for _ in range(num_cubes)]

    # continuously check the location of the cubes to see if the opponent has captured one of them
    while robot1_score or robot2_score is not max_score:
        # receive the other player's cube locations and use is_in_base to compare positions for scoring purposes
        coordinates: List[str] = receive_message(connection)

        # unpack robot 2's coordinates from the network message
        robot2_x_coordinates: List[float] = [float(coord) for i, coord in enumerate(coordinates) if i % 2 is not 0]
        robot2_y_coordinates: List[float] = [float(coord) for i, coord in enumerate(coordinates) if i % 2 is 0]
        robot2_coordinates: List[Tuple[float, float]] = list(zip(robot2_x_coordinates, robot2_y_coordinates))

        # unpack robot 1's coordinates to check them against robot 2's origin
        robot1_coordinates: List[Tuple[float, float]] = []
        for cube in range(len(robot_cubes)):
            cube_pos: cozmo.util.Pose = robot_cubes[cube].pose
            robot1_coordinates.append((cube_pos.position.x, cube_pos.position.y))

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
            # send the reset message over the network to make robot 2 reset its coordinates
            connection.send(b'Resetting')
            time.sleep(15)

        if robot2_score % num_cubes == 0:
            # send the reset message over the network to make the slave computer's thread sleep
            connection.send(b'Reset')
            reset(robot_cubes, robot)

    # someone won the game, make the slave computers exit execution
    connection.send(b'Exit')

    # print the win state
    if robot1_score == max_score:
        print('Robot 1 won!')
    else:
        print('Robot 2 won!')


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


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
