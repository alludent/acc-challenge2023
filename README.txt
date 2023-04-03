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

Design =====================================================================================================================================================================
Assets: Models, textures
Main:
  creates Ursina window
  creates the player, the gun, and the grapple gun
  creates the world
  Update function respawns enemies every 45 seconds. Also checks for left and right mouse inputs
  Defines player functions (shoot, grapple)
Menu:
  This is the main menu screen. 
FirstPersonController
  player control (WASD) as well as player variables (gravity, jump height, speed, etc)
  mouse control for the camera
  Also detects collisions using ray cast
UI:
  handles death screen and pausing 

Start Screen
Gameplay
End Screen
The main game loop at this level has three roles:

Pull events off of the event queue (e.g. exit, mouse input, game state change) and handle
Tell current active game state mgr to update for the current frame (more on that below)
Sleep for the specified FPS amount
Start Screen Manager
This game state manager simply manages the start screen view and listens for it's "start" button to be clicked. On click, we push a custom "ON_START_GAME" event into the PyGame event queue for Main to handle on the next loop iteration and transition its active game state.

Gameplay Manager
This manager is in charge of the actual game activity. It contains a "player_paddle" component, "ai_paddle" component, and "ball" component and controls activity around each. On each loop iteration, this manager executes the following actions:

Update:
Update ball and paddle positions
Detect and handle ball collisions
Detect and handle ball passing bounds and updating score
Detect and handle score passing max score threshold (triggering end of game event)
Draw:
Trigger each component's drawing logic, based on its updated positioning
End Screen Manager
Similar to Start Screen, this shows up after the end of a game with a single button to trigger returning to main game screen.
