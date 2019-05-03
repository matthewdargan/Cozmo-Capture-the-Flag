# Cozmo Capture the Flag Game Mode
## Overview
This is an interactive Python project that allows users to play a Capture the Flag game mode with other users.
Users will be able to control their Cozmos with an Xbox controller.

## Installation
To run this project:

1. Clone this repository from the terminal with `git clone https://github.com/matthewdargan/Cozmo-Capture-the-Flag.git`
or download it into a zip file by clicking
[here](https://github.com/matthewdargan/Cozmo-Capture-the-Flag/archive/master.zip)
2. Navigate to the directory where you cloned the repo or unzipped the repository.
3. Install the required dependencies with `pip install -r requirements.txt`.
4. Execute `python judge.py` from the terminal to enable the main computers to establish a connect
to the robot from your mobile device and begin using the controller. Execute `python player.py`
to enable the secondary computers to connect to their robots and begin using the controllers.

**Note: You must install [Xboxdrv](https://github.com/xboxdrv/xboxdrv) in order to use an Xbox 360 controller
on a Linux device; however, Windows devices do not require any 3rd party driver. The Linux driver only supports
the Xbox 360 controller but the Windows driver supports both Xbox 360 and Xbox One controllers (wired or wireless).**

## Requirements
* A TCP network to play with more than one other player
* At least two Xbox controllers
* At least four Cozmos and four computers
* At least four Android or iOS devices and a USB cable to connect the device to a computer to run the game logic

## TODO
- [ ] Abstractions for interactions between more than 2 Cozmos
- [ ] Finish Judge logic 
- [ ] Setup the player scripts asynchronously to run the xbox controller modules and listen for messages on the network

## Dependencies
* [Xbox Controller Interface for Cozmo](https://github.com/matthewdargan/Cozmo-Xbox-Controller)
* [Xbox Controller Module for Linux](https://github.com/FRC4564/Xbox)
* [Xboxdrv - for Linux based systems](https://github.com/xboxdrv/xboxdrv)
* [Cozmo SDK](http://cozmosdk.anki.com/docs/)
