from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import geopy
from geopy.distance import VincentyDistance
from math import sin, radians

# Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect('udpin:0.0.0.0:14550')


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

        
    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True    

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt 
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
            print "Reached target altitude"
            break
        time.sleep(1)


def condition_yaw(heading, relative=False):
    """
    Send MAV_CMD_CONDITION_YAW message to point vehicle at a specified heading (in degrees).

    This method sets an absolute heading by default, but you can set the `relative` parameter
    to `True` to set yaw relative to the current yaw heading.

    By default the yaw of the vehicle will follow the direction of travel. After setting 
    the yaw using this function there is no way to return to the default yaw "follow direction 
    of travel" behaviour (https://github.com/diydrones/ardupilot/issues/2427)

    For more information see: 
    http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
    """
    if relative:
        is_relative = 1 #yaw relative to direction of travel
    else:
        is_relative = 0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)


def goto(targetLocation):
    """
    """

    currentPoint = geopy.Point(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
    targetPoint = geopy.Point(targetLocation.lat, targetLocation.lon)
    targetDistance = VincentyDistance(currentPoint, targetPoint).meters
    vehicle.simple_goto(targetLocation, groundspeed=1)
    
    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        currentPoint = geopy.Point(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        remainingDistance = VincentyDistance(currentPoint, targetPoint).meters
        print "Distance to target: ", remainingDistance
        if remainingDistance<=1.0: # Near enough
            print "Reached target"
            break;
        time.sleep(2)


print "home heading: ", vehicle.heading
homeHeading = vehicle.heading
homePoint = geopy.Point(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)

# determine the marker locations
frontRightMarker = VincentyDistance(meters=int(5/sin(radians(45)))).destination(homePoint, (homeHeading + 45) % 360)
frontLeftMarker = VincentyDistance(meters=10).destination(frontRightMarker, (homeHeading - 90) % 360)
backLeftMarker = VincentyDistance(meters=10).destination(frontLeftMarker, homeHeading)
backRightMarker = VincentyDistance(meters=10).destination(backLeftMarker, (homeHeading + 90) % 360)

targetAltitude = 3
arm_and_takeoff(targetAltitude)

print("Move to the front-right marker...")
targetPoint = frontRightMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))
condition_yaw(homeHeading) # aircraft heading will remain constant

time.sleep(2)

print("Move to the front-left marker and back again...")
targetPoint = frontLeftMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = frontRightMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

time.sleep(2)

print("Move to each marker, maintaining altitude...")
targetPoint = frontLeftMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = backLeftMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = backRightMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = frontRightMarker
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

time.sleep(2) # enjoy the moment

print("Perform the vertical rectangle...")
targetPoint = frontLeftMarker
targetAltitude = 3
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = frontLeftMarker
targetAltitude = 8
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))
# Wait until the vehicle reaches the target altitude before processing the next goto
while True:
    print " Altitude: ", vehicle.location.global_relative_frame.alt 
    if (vehicle.location.global_relative_frame.alt >= targetAltitude*0.95) and (vehicle.location.global_relative_frame.alt <= targetAltitude*1.05):
        print "Reached target altitude"
        break
    time.sleep(1)

targetPoint = frontRightMarker
targetAltitude = 8
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = frontRightMarker
targetAltitude = 3
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))
# Wait until the vehicle reaches the target altitude before processing the next goto
while True:
    print " Altitude: ", vehicle.location.global_relative_frame.alt 
    if (vehicle.location.global_relative_frame.alt >= targetAltitude*0.95) and (vehicle.location.global_relative_frame.alt <= targetAltitude*1.05):
        print "Reached target altitude"
        break
    time.sleep(1)

time.sleep(2) # enjoy the moment

print("Perform the trapezoid...")
targetPoint = frontLeftMarker
targetAltitude = 3
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = backLeftMarker
targetAltitude = 8
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = backRightMarker
targetAltitude = 8
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

targetPoint = frontRightMarker
targetAltitude = 3
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=targetAltitude))

time.sleep(2) # enjoy the moment

print("Return to take-off position and land...")
targetPoint = homePoint
goto(LocationGlobalRelative(targetPoint.latitude, targetPoint.longitude, alt=2))

print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")

# Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()
