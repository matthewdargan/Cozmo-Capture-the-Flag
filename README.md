# Cozmo Capture the Flag Game Mode
## Overview
This is a Python project that allows users to play a Capture the Flag game mode either with other users or with the CPU. Users will be able to control their
Cozmos with an Xbox 360 controller or with the controls in the mobile app for Cozmo.

## Installation
To run this project:

1. Clone this repository from the terminal with `git clone https://github.com/matthewdargan/Cozmo-Capture-the-Flag.git` or download it into a zip file by clicking:
[link](https://github.com/matthewdargan/Cozmo-Capture-the-Flag/archive/master.zip)
2. Navigate to the directory where you cloned the repo or unzipped the repository.
3. Install the required dependencies with `pip install -r requirements.txt`.
4. Execute `python capture_the_flag.py` from the terminal to establish a connect to the robot from your mobile device and begin using the controller.

**Note: You must install [Xboxdrv](https://github.com/xboxdrv/xboxdrv) in order to use an Xbox 360 controller on a Linux device; however, Windows devices do not require any 3rd party driver.**

## Dependencies
* [Xbox 360 Controller Interface for Cozmo](https://github.com/matthewdargan/Cozmo-Xbox-Controller)
* [Xbox Controller Module](https://github.com/FRC4564/Xbox)
* [Xboxdrv - for Linux based systems](https://github.com/xboxdrv/xboxdrv)
* [Cozmo SDK](http://cozmosdk.anki.com/docs/)
