# solo
Some scripts for the 3DR Solo

References
+ http://python.dronekit.io/develop/sitl_setup.html
+ http://dronecode.github.io/MAVProxy/html/getting_started/download_and_installation.html
+ http://dev.3dr.com/starting-installing.html

Installing
+ git clone http://github.com/dronekit/dronekit-python.git
+ pip install --upgrade pip
+ sudo pip install dronekit
+ sudo pip install dronekit-sitl -UI
+ brew tap homebrew/science
+ brew install wxmac wxpython opencv
+ sudo pip uninstall python-dateutil
+ sudo pip install numpy pyparsing
+ sudo pip install MAVProxy

Start the simulator, listening on port 5760
+ dronekit-sitl solo-1.2.8 (see http://dronekit-assets.s3-website-us-east-1.amazonaws.com/sitl/solo/)

Start MAVProxy with a map and console, connect to the simulator, and allow connections to the simulator on port 14550
+ mavproxy.py --master tcp:127.0.0.1:5760 --out 127.0.0.1:14550 --console --map

Run the DroneKit script
+ cd ~/dronekit-python/examples/simple_goto
+ pip install geopy -UI
+ python simple_goto.py --connect 127.0.0.1:14550

Building a new version of SITL
+ brew tap homebrew/versions
+ brew install gcc48 gawk
+ sudo easy_install pip
+ sudo pip install awscli virtualenv
+ python setup.py install
+ ./build.sh solo 1.2.19 (see https://github.com/dronekit/dronekit-sitl/tree/master/stage)
+ … getting the list of tagged releases from https://github.com/tcr3dr/ardupilot-releases/releases

Then to run SITL...
+ dronekit-sitl /Users/daryl/dronekit-sitl/stage/build/staging/ArduCopter.elf
