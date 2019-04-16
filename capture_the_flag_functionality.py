import multiprocessing
import platform
import socket
import time
from typing import List

import cozmo
from cozmo.objects import LightCube, LightCube1Id, LightCube2Id, LightCube3Id

from linux_tools import cozmo_interface
from message_forwarder import start_connection, receive_message
from windows_tools import xbox_controller


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
