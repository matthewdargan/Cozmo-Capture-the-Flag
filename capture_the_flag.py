"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

import multiprocessing
import platform
import time

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id

import cozmo_interface
import xbox_controller


async def cozmo_program(robot1: cozmo.robot.Robot, robot2: cozmo.robot.Robot):
    """
    TODO: comment main function
    """
    while True:
        try:
            num_cubes = int(input("How many cubes do you want to play with?"))
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

    robot1_cubes = []
    robot2_cubes = []

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

    for cube in range(len(robot1_cubes)):
        robot1_cubes[cube].set_lights(cozmo.lights.blue_light)
        robot2_cubes[cube].set_lights(cozmo.lights.red_light)

    while True:
        try:
            max_score = int(input("How many points do you want to play up to?"))
        except ValueError:
            print("Invalid input type")
            continue
        if max_score < 0:
            print("Input must be positive")
            continue
        else:
            break

    print("Set Cozmo's in position to play.")
    time.sleep(10)
    robot1_origin = robot1.pose
    robot2_origin = robot2.pose
    origin_boundary = (300, 300, 0)
    print("Start playing!")

    # allow the users to start controlling the robots here
    if get_platform() == 'Windows':
        multiprocessing.Process(target=xbox_controller.cozmo_program()).start()
    else:
        multiprocessing.Process(target=cozmo_interface.cozmo_program()).start()

    robot1_score = 0
    robot2_score = 0
    robot1_acquire_status = False
    robot2_acquire_status = False

    # continuously check the location of the cubes to see if the opponent has captured one of them
    while robot1_score or robot2_score is not max_score:
        (robot1_acquire_status, robot2_acquire_status) = is_in_base(robot1_cubes, robot2_cubes, origin_boundary)

        if robot1_acquire_status:
            robot1_score += 1
        if robot2_acquire_status:
            robot2_score += 1

        # if all of the cubes have already been found, let the users reset the locations and then resume playing
        if robot1_score % num_cubes == 0:
            reset(robot1_cubes)
        if robot2_score % num_cubes == 0:
            reset(robot2_cubes)


def get_platform():
    """
    Get the operating system that the user is on so we call the correct xbox controller functionality script

    :return: a string containing the operating system that the user is on
    """
    if platform.system() == 'Windows':
        # run xbox_controller script asynchronously
        return 'Windows'
    else:
        # run cozmo_interface asynchronously
        return 'Linux'


def is_in_base(robot1_cubes, robot2_cubes, origin_boundary):
    """
    Check the location of the cube relative to an opponent's base

    :return: a conditional tuple containing the cube acquirement statuses for robot1 and robot2
    """
    robot1_cond = False  # if a cube is in robot 1's base
    robot2_cond = False  # if a cube is in robot 2's base

    for cube in range(len(robot1_cubes)):
        cube1_position = robot1_cubes[cube].Position
        cube2_position = robot2_cubes[cube].Position

        for position in range(len(cube1_position)):
            # set robot 2's base condition to true if one of robot 1's cube's is in its base
            if cube1_position[position] <= origin_boundary[position] or cube1_position[position] >= 0:
                robot2_cond = True

            # set robot 1's base condition to true if one of robot 2's cube's is in its base
            if cube2_position[position] <= origin_boundary[position] or cube2_position[position] >= 0:
                robot1_cond = True

    return robot1_cond, robot2_cond


def reset(robot_cubes):
    """
    Reset the game state so that we allow the user to re-hide their cubes and them continue playing

    :param robot_cubes: one of the robots cubes that need to be reset
    :return:
    """
    # TODO: allow a user to reset the locations of however many cubes are being used using time.sleep(...)
    #       sleep the controller thread as well to prevent players from controller the robots during reset time


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
