"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

from typing import List, Tuple
from itertools import permutations
import multiprocessing
import platform
import time

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id, LightCube

from linux_tools import cozmo_interface
from windows_tools import xbox_controller


async def cozmo_program(robot1: cozmo.robot.Robot, robot2: cozmo.robot.Robot):
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

    # TODO: use robot origins to set their own boundaries with x, y + 300 as the max coordinates

    # set the capture boundaries for stealing an opponent's cubes with coordinates forming a box
    perm = permutations([0, 300, 0, 300], 2)
    origin_boundaries: List[Tuple[int]] = list(set(perm))

    print("Start playing!")

    # allow the users to start controlling the robots here
    if get_platform() == 'Windows':
        # TODO: figure out whether we want one thread or separate threads for the controller states
        #  for the different robots
        multiprocessing.Process(target=xbox_controller.cozmo_program(robot1)).start()
        multiprocessing.Process(target=xbox_controller.cozmo_program(robot2)).start()
    else:
        multiprocessing.Process(target=cozmo_interface.cozmo_program(robot1)).start()
        multiprocessing.Process(target=cozmo_interface.cozmo_program(robot2)).start()

    # set default scores for each side
    robot1_score: int = 0
    robot2_score: int = 0

    # continuously check the location of the cubes to see if the opponent has captured one of them
    while robot1_score or robot2_score is not max_score:
        # get the current statuses for whether a new cube of the opponent is in the user's base
        # TODO: possibly fix is_in_base to be relative to each robot's positions
        (robot1_acquire_status, robot2_acquire_status) = is_in_base(robot1_cubes, robot2_cubes, origin_boundary)

        # if a user has acquired one of the opponent's cubes then increment their score
        if robot1_acquire_status:
            robot1_score += 1
        if robot2_acquire_status:
            robot2_score += 1

        # if all of the cubes have already been found, let the users reset the locations and then resume playing
        if robot1_score % num_cubes == 0:
            reset(robot2_cubes, robot2)
        if robot2_score % num_cubes == 0:
            reset(robot1_cubes, robot1)


def get_platform() -> str:
    """
    Get the operating system that the user is on so we call the correct xbox controller functionality script.

    :return: a string containing the operating system that the user is on
    """
    if platform.system() == 'Windows':
        # run xbox_controller script asynchronously
        return 'Windows'
    else:
        # run cozmo_interface asynchronously
        return 'Linux'


def is_in_base(robot1_cubes: List[LightCube], robot2_cubes: List[LightCube], origin_boundaries: List[Tuple[int]]) -> Tuple[bool, bool]:
    """
    Check the location of the cube relative to an opponent's base.

    :return: a conditional tuple containing the cube acquirement statuses for robot1 and robot2
    """
    robot1_cond: bool = False  # if a cube is in robot 1's base
    robot2_cond: bool = False  # if a cube is in robot 2's base

    for cube in range(len(robot1_cubes)):
        cube1_position: cozmo.util.Position = robot1_cubes[cube].pose.Position
        cube2_position: cozmo.util.Position = robot2_cubes[cube].pose.Position

        # TODO: make the boundary a box (0, 0) ... (300, 300)
        # iterate through the x, y, and z coordinates of the Position of the cubes
        for i, _ in enumerate(cube1_position.x_y_z):
            if i == 0:
                # set robot 2's base condition to true if one of robot 1's cube's is in its base
                if cube1_position.x <= origin_boundary[i] or cube1_position.x >= 0:
                    robot2_cond = True

                # set robot 1's base condition to true if one of robot 2's cube's is in its base
                if cube2_position.x <= origin_boundary[i] or cube2_position.x >= 0:
                    robot1_cond = True
            elif i == 1:
                if cube1_position.y <= origin_boundary[i] or cube1_position.y >= 0:
                    robot2_cond = True

                if cube2_position.y <= origin_boundary.[i] or cube2_position.y >= 0:
                    robot1_cond = True
            else:
                if cube1_position.z <= origin_boundary[i] or cube1_position.z >= 0:
                    robot2_cond = True

                if cube2_position.z <= origin_boundary.[i] or cube2_position.z >= 0:
                    robot1_cond = True

    return robot1_cond, robot2_cond


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
