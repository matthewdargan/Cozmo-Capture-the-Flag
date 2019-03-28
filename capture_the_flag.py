"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

import cozmo
from cozmo.util import degrees
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
import platform
import subprocess
import sys

import cozmo_interface
import xbox_controller
from colors import Colors

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

    for cube_num in len(num_cubes):
        if cube_num == 1:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube1Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube1Id))
        elif cube_num == 2:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube2Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube2Id))
        else:
            robot1_cubes.append(robot1.world.get_light_cube(LightCube3Id))
            robot2_cubes.append(robot2.world.get_light_cube(LightCube3Id))
   
 
if __name__ == '__main__':
    if platform.system() == 'Windows':
        # run xbox_controller script asynchronously
        subprocess.Popen([sys.executable, xbox_controller.cozmo_program], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        # run cozmo_interface asynchronously
        subprocess.Popen([sys.executable, cozmo_interface.cozmo_program], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    
    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)
