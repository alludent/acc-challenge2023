Robot Rampage created by Wu, Deric, Chris, Albert 

Robot Rampage ========================================================================================================================================================

This project was developed using Python 3.10.1. "main.pyw" serves as the entrypoint to the application. The "requirements.txt" file includes all dependencies required in this project - to install all dependencies listed in this file, run the following command from command line:

py -m pip install -r requirements.txt

How to Play ==========================================================================================================================================================
Shoot: Left click
Grapple: Right click
Move: WASD
Jump: Space
Pause: Escape

Design ===============================================================================================================================================================
Assets: 
  Models, textures
Main:
  creates Ursina window
  creates the player, the gun, and the grapple gun
  creates the world
  Defines player functions (shoot, grapple)
  (FUNC) UPDATE:
    respawns enemies every 45 seconds
    checks for left and right mouse inputs
Menu:
  This is the main menu screen. 
FirstPersonController
  contains player variables (hp, gravity, jump height, speed, etc)
  (FUNC) UPDATE:
    checks for movement inputs (WASD)
    manages mouse control for the camera
    detects collisions using ray cast
UI:
  manages death screen, menus, and player healthbar
Enemy:
  contains enemy mechanics (move towards player, leap), enemy variables(hp, speed, target, gravity, etc)
  (FUNC) UPDATE:
    calculate enemy distance to target, move accordingly
    attack the target
    leap towards the target

