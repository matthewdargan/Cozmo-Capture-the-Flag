"""Capture the Flag game mode for cozmo
Authors: Matthew Dargan, Daniel Stutz
"""

import cozmo
from cozmo.util import degrees
import platform

import cozmo_interface
import xbox_controller
from colors import Colors

async def cozmo_program(robot: cozmo.robot.Robot):
    """
    TODO: comment main function
    """
    
    pass

if __name__ == '__main__':
    if platform.system() == 'Windows':
        # run xbox_controller script asynchronously

    else:
        # run cozmo_interface asynchronously

    cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)

