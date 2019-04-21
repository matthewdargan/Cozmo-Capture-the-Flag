import socket
import time
from typing import List

import cozmo

from capture_the_flag_functionality import setup, reset
from message_forwarder import start_connection, receive_message


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light):
    """
    Main entry point for running the slave logic for the capture the flag game.

    TODO: abstract this out so its a list of up to 4 robots
    :param robot: a secondary robot in the game
    :param cube_color color for this team's cubes
    """

    # setup connection to the network
    connection: socket.socket = start_connection("10.0.1.10", 5000)

    # get the number of cubes that should be connected to the secondary robot
    num_cubes: int = int(receive_message(connection)[0][0])

    start_message: List[List[str]] = receive_message(connection)

    # wait for the start message on the network
    while 'Start' not in start_message:
        start_message = receive_message(connection)

    # setup the game
    connection, robot_cubes, robot_origin = setup(robot, num_cubes, cube_color)

    new_message = receive_message(connection)

    while 'Exit' not in new_message:
        # sleep for 15 seconds if the main robot needs to reset
        if 'Reset' in new_message:
            time.sleep(15)

        # reset this robot
        elif 'Resetting' in new_message:
            reset(robot_cubes, robot)

        # run normally by sending the cube positions out constantly to the network
        cube1_pos = robot_cubes[0].pose.Position
        cube2_pos = robot_cubes[1].pose.Position
        cube3_pos = robot_cubes[2].pose.Position

        connection.send(b'Robot2, %f, %f, %f, %f, %f, %f'
                        % (cube1_pos.x, cube1_pos.y, cube2_pos.x, cube2_pos.y, cube3_pos.x, cube3_pos.y))
        new_message = receive_message(connection)

    # exit the game, someone won the game
    robot.say_text('Game over!')


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
