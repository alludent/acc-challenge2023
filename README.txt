Robot Rampage created by Wu, Deric, Chris, Albert 

convert files to exe -> 
pyinstaller --noconfirm --onefile --windowed --add-data "Enemy.py;." --add-data "FirstPersonController.py;." --add-data "UI.py;." --add-data "Assets;Assets/" --add-data "Lib/panda3d;panda3d/"--add-data "Lib/panda3d-1.10.13.dist-info;panda3d-1.10.13.dist-info/" --add-data "Lib/direct;direct/" --add-data "Lib/ursina;ursina/" --add-data "Lib/ursina-5.2.0.dist-info;ursina-5.2.0.dist-info/" --name=RobotRampage  main.py
