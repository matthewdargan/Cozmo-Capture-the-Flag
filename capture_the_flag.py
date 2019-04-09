"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

import multiprocessing
import platform
import time
from typing import List

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id, LightCube

from linux_tools import cozmo_interface
from windows_tools import xbox_controller


def cozmo_program(robot1: cozmo.robot.Robot, robot2: cozmo.robot.Robot):
    """
    Main entry point for running the logic for the capture the flag game.

    TODO: abstract this out so its a list of up to 4 robots
    :param robot1: first robot in the game
    :param robot2: second robot in the game
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

    # lists for storing robot1's and robot2's cubes
    robot1_cubes: List[LightCube] = []
    robot2_cubes: List[LightCube] = []

    # add the cubes to their respective lists
    for cube_num in range(num_cubes):
        if cube_num == 1:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube1Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube1Id))
        elif cube_num == 2:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube2Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube2Id))
        else:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube3Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube3Id))

    # set the colors for robot1's cubes to blue and robot2's to red
    for cube in range(len(robot1_cubes)):
        robot1_cubes[cube].set_lights(cozmo.lights.blue_light)
        robot2_cubes[cube].set_lights(cozmo.lights.red_light)

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

    print("Set Cozmo's in position to play.")

    # give a 10 second period for the users to set their robots in their bases and hide their cubes
    time.sleep(10)

    # get robot1's and robot2's origins
    robot1_origin: cozmo.util.Pose = robot1.pose
    robot2_origin: cozmo.util.Pose = robot2.pose

    print("Start playing!")

    # allow the users to start controlling the robots here
    if platform.system() == 'Windows':
        multiprocessing.Process(target=xbox_controller.cozmo_program(robot1)).start()
        multiprocessing.Process(target=xbox_controller.cozmo_program(robot2)).start()
    else:
        multiprocessing.Process(target=cozmo_interface.cozmo_program(robot1)).start()
        multiprocessing.Process(target=cozmo_interface.cozmo_program(robot2)).start()

    # set default scores for each side
    robot1_score: int = 0
    robot2_score: int = 0

    # previous lists of the cube statuses for each of the robots
    robot1_prev_statuses: List[bool] = [False for _ in range(num_cubes)]
    robot2_prev_statuses: List[bool] = [False for _ in range(num_cubes)]

    # continuously check the location of the cubes to see if the opponent has captured one of them
    while robot1_score or robot2_score is not max_score:
        # get the current statuses for whether a new cube of the opponent is in the user's base
        robot1_acquire_statuses: List[bool] = is_in_base(robot2_cubes, robot1_origin.position)
        robot2_acquire_statuses: List[bool] = is_in_base(robot1_cubes, robot2_origin.position)

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
            reset(robot2_cubes, robot2)

        if robot2_score % num_cubes == 0:
            reset(robot1_cubes, robot1)


def is_in_base(robot_cubes: List[LightCube], base_boundaries: cozmo.util.Position) -> List[bool]:
    """
    Check the location of the cubes relative to an opponent's base.

    :return: a list of booleans corresponding to the cube acquirement statuses for a robot
    """
    robot_cond: List[bool] = [False for _ in range(len(robot_cubes))]

    for cube in range(len(robot_cubes)):
        cube_position: cozmo.util.Position = robot_cubes[cube].pose.Position

        if 0 <= cube_position.x <= base_boundaries.x + 300 and 0 <= cube_position.y <= base_boundaries.y + 300:
            robot_cond[cube] = True

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
