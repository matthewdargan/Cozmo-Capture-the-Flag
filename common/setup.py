import time
from typing import List, Dict

import cozmo
from cozmo.objects import LightCube, LightCube1Id, LightCube2Id, LightCube3Id


def setup(robot: cozmo.robot.Robot, cube_color: cozmo.lights.Light) -> (List[LightCube]):
    """
    Setup up the cozmo program to run for each computer to use.

    :param robot robot to get cubes for
    :param cube_color color of this team's cubes
    """

    # store all of the cube objects in a list
    robot_cubes: List[LightCube] = [robot.world.get_light_cube(LightCube1Id), robot.world.get_light_cube(LightCube2Id),
                                    robot.world.get_light_cube(LightCube3Id)]

    # set the colors for robot1's cubes to blue and robot2's to red
    for cube in range(len(robot_cubes)):
        robot_cubes[cube].set_lights(cube_color)

    # start the game once the master computer sends out the start message over the network
    print("Set Cozmo's in position to play.")

    # give a 10 second period for the users to set their robots in their bases and hide their cubes
    time.sleep(10)

    print("Start playing!")

    return robot_cubes


def get_team_colors(teams: int) -> (Dict[int, cozmo.lights.Light], Dict[int, cozmo.lights.Light]):
    """
    Gets the team colors and opponent colors based on the number of teams playing in the game.

    :param teams: number of teams playing in the game
    :return: the team colors and the opponent colors
    """
    team_colors: Dict[int, cozmo.lights.Light] = {1: cozmo.lights.red_light, 2: cozmo.lights.blue_light}
    opponent_colors: Dict[int, cozmo.lights.Light] = {1: cozmo.lights.blue_light, 2: cozmo.lights.red_light}

    if teams == 3:
        team_colors[3] = cozmo.lights.green_light
        opponent_colors: Dict[int, cozmo.lights.Light] = {1: cozmo.lights.green_light, 2: cozmo.lights.red_light,
                                                          3: cozmo.lights.blue_light}

    return team_colors, opponent_colors
