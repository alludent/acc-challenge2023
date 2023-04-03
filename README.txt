Robot Rampage created by Wu, Deric, Chris, Albert 

Robot Rampage ========================================================================================================================================================

This project was developed using Python 3.10.1. "main.py" serves as the entrypoint to the application. The "requirements.txt" file includes all dependencies required in this project - to install all dependencies listed in this file, run the following command from command line:

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
    checks for left and right mouse inputs and acts accordingly
  (FUNC) GRAPPLE:
    determines when to grapple
    determines if something was grappled using raycast
    pulls the player towards the point of impact
    makes sure the player doesn't collide with anything using top and bottom raycast
    player stays at the point of impact until release right mouse
  (FUNC) RELEASE_GRAPPLE():
    called when player releases right click
    resets to default variables associated with not grappling
  (FUNC) SHOOT():
    if camera center(mouse) is hovered over an entity, decrease that entitie's hp
    
Menu:
  This is the main menu screen. 
FirstPersonController
  contains player variables (hp, gravity, jump height, speed, etc)
  (FUNC) UPDATE:
    checks for movement inputs (WASD)
    manages mouse control for the camera
    detects collisions using ray cast from the top of the player and bottom of the player
UI:
  manages death screen, menus, and player healthbar
Enemy:
  contains enemy mechanics (move towards player, leap), enemy variables(hp, speed, target, gravity, etc)
  (FUNC) UPDATE:
    calculate enemy distance to target, move accordingly
    attack the target
    leap towards the target

