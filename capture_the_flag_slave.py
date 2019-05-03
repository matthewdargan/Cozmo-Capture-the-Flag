import socket
import time

import cozmo

from capture_the_flag_functionality import setup, reset
from message_forwarder import start_connection, receive_message


def cozmo_program(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light = cozmo.lights.red_light):
    """
    Main entry point for running the slave logic for the capture the flag game.

    :param robot: a secondary robot in the game
    :param cube_color color for this team's cubes
    """

    # setup connection to the network
    connection: socket.socket = start_connection("10.0.1.10", 5000)

    # get the number of cubes that should be connected to the secondary robot
    num_cubes: int = int(receive_message(connection)[0])

    # setup the game
    robot_cubes, robot_origin = setup(robot, num_cubes, cube_color)

    # send robot 2's origin over the network to calibrate relativity
    connection.send(b'%f %f' % (robot_origin.position.x, robot_origin.position.y))

    # get the cube positions
    cube1_pos = robot_cubes[0].pose
    # cube2_pos = robot_cubes[1].pose
    # cube3_pos = robot_cubes[2].pose

    # default the message from master as None
    new_message = []

    while 'Exit' not in new_message:
        print(new_message)
        # sleep for 15 seconds if the main robot needs to reset
        if 'Reset' in new_message:
            time.sleep(15)

        # reset this robot
        elif 'Resetting' in new_message:
            reset(robot_cubes, robot)

        # run normally by sending the cube positions out constantly to the network
        cube1_pos = robot_cubes[0].pose
        # cube2_pos = robot_cubes[1].pose
        # cube3_pos = robot_cubes[2].pose

        connection.send(b'%f %f' % (cube1_pos.position.x, cube1_pos.position.y))

        new_message = receive_message(connection)

    # exit the game, someone won the game
    robot.say_text('Game over!')


if __name__ == '__main__':
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
