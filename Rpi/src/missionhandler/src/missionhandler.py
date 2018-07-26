import RPi.GPIO as GPIO
import rospy
import mavros
import mavros_msgs
from mavros_msgs.msg import VFR_HUD
import nav_msgs
from std_msgs.msg import String
from sensor_msgs.msg import Imu, NavSatFix, NavSatStatus
import math


vfr_data = []
nav_data = []
waypoint_data = []


class Waypoint:
    def __init__(self, mission_id, lat, lon, height, isCnt):
        self.mission_id = missio
        self.lat = lat
        self.lon = lon
        self.height = height
        self.isCnt = isCnt
        

class Navstatus:
    def __init__(self, lat, lon, alt, xac, yac, zac):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.xac = xac
        self.yac = yac
        self.zac = zac       


class vfr:
    def __init__(self, airspeed, groundspeed, heading, throttle, altitude, climb):
        self.airspeed = airspeed
        self.groundspeed = groundspeed
        self.heading = heading
        self.throttle = throttle
        self.altitude = altitude
        self.climb = climb