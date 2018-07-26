import rospy
import mavros
import mavros_msgs
import nav_msgs
from std_msgs.msg import String
from sensor_msgs.msg import Imu, NavSatFix, NavSatStatus, BatteryState, Temperature
import math
from datetime import datetime
import time



mission_id = 0
mission_data = []
nav_data = []
sensor_data = []
flight_data = []
system_data = []
batt_data = []
xacc = 0
yacc = 0
zacc = 0
lati = 0
longi = 0
alti = 0
temp_data = 0
land_pos = {"lat": 0, "lon": 0}


current_state = State() 

def state_cb(state):
    global current_state
    current_state = state

class Mission:
    def __init__(self, mission_id, cycle, lat, lon, height, weight):
        self.mission_id = mission_id
        self.cycle = cycle
        self.lat = lat
        self.lon = lon
        self.height = height
        self.weight = weight

class Navstatus:
    def __init__(self, lat, lon, alt, xac, yac, zac):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.xac = xac
        self.yac = yac
        self.zac = zac

class SensorStatus:
    def __init__(self, pressure, motor_cycle, roll, pitch, yaw, wind):
        self.pressure = pressure
        self.motor_cycle = motor_cycle
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.wind = wind


class flightStatus:
    def __init__(self, flightMode, flightTime, flight_remaining, mission_info):
        self.flightMode = flightMode
        self.flightTime = flightTime
        self.flight_remaining = flight_remaining
        self.mission_info = mission_info

class sytemStatus:
    def __init__(self, error_info, currentConsump):
        self.error_info = error_info
        self.currentConsump = currentConsump
        

class batteryStat:
    def __init__(self, batcurrent, batt):
        self.batcurrent = batcurrent
        self.batt = batt

class subscriberListener(rospy.SubscribeListener):
    def peer_subscribe(self, topic_name, topic_publish, peer_publish):
        print("a peer subscribed to topic [%s]"%topic_name)
        str = "Joined topic "+topic_name
        print(str)
        peer_publish(String(str))
        
    def peer_unsubscribe(self, topic_name, numPeers):
        print("a peer unsubscribed from topic [%s]"%topic_name)
        if numPeers == 0:
            print("Topic has no subscriber")


pub_general = rospy.Publisher('/rpi/sensorhandler', String, queue_size=50, subscriber_listener=subscriberListener())
pub_system = rospy.Publisher('/rpi/system', String, queue_size=20, subscriber_listener=subscriberListener())

def ros_start(node):
    rospy.init_node(node , anonymous=True)

def request(data):
    req = data.data
    
    if req:
        i, cyc, lt, ln, hgh, wght = mission_data[mission_id]
        distance = math.sqrt((lt - lati)**2 + (ln - longi)**2)
        xtime = abs(lt - lati) / xacc
        ytime = abs(ln - longi) / yacc

        #This not required but I added that because of after takeoff calculations
        #Locations can be measured from sea level and some coordinates is greater than 
        #actual position.I want to avoid that error.
        ztime = (abs(alti - hgh) / zacc) + (abs(alti - hgh)/wght*9.8)

        totaltime = math.sqrt(xtime**2 + ytime**2 + ztime**2)
        
        line1 = abs(0-math.sqrt(lt**2 + ln**2))
        line2 = abs(0-math.sqrt(lt**2 + ln**2))
        angle = math.asin(math.sqrt(line1**2 + line2**2))

        flmode, fltime, flrmn, info = flight_data[-1]
        pres, mtr_cyc, rll, ptch, yw, wnd = sensor_data[-1]
        latitude, longitude, altitude, xa, ya, za = nav_data[-1]
        
        #Status data will be like [flight_mode-flight_time-arrive-mission_id-angle-lat-lon-altitude-xaccel-yaccel-zaccel-pressure-motor_cycle-roll-yaw-pitch-wind]
        pub_general.publish("'{}'-".format(flmode)+fltime+"-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'-'{}'".format(
            flrmn, mission_id, angle, latitude, longitude, altitude, xa, ya, za, pres, mtr_cyc, rll, ptch, yw, wnd
        ))

def systemStat():


def getFlightData():
    flmode = current_state
    
    fltime = time.asctime(time.time)

    x = land_pos["lat"]
    y = land_pos["lon"]
    distance = math.sqrt((x - lati)**2 + (y - longi)**2)
    xtime = abs(x - lati) / xacc
    ytime = abs(y - longi) / yacc

    #This not required but I added that because of after takeoff calculations
    #Locations can be measured from sea level and some coordinates is greater than 
    #actual position.I want to avoid that error.

    totaltime = math.sqrt(xtime**2 + ytime**2 )
    flrmn = totaltime
    flight_data.append(flightStatus(flmode, fltime, flrmn))


def getBatData(data):
    current = data.current
    percentage = data.percentage
    batt_data.append(batteryStat(current, percentage))



def getMission(data):
    #Data format should be [mission.id-cycle-lat-lon-height-ballweight]
    rawData = data.data
    splitted = rawData.split("-")
    mission_id = int(splitted[0])
    cycle = int(splitted[1])
    lat = float(splitted[2])
    lon = float(splitted[3])
    height = int(splitted[4])
    weight = float(splitted[5])
    mission_data.append(Mission(mission_id,cycle, lat, lon, height, weight))


def ImuData(data):
    xacc, yacc, zacc = data.linear_acceleration.x, data.linear_acceleration.y, data.linear_acceleration.z
    nav_data.append(Navstatus(lati, longi, alti, xacc, yacc, zacc))

def getNavData(data):
    lati = data.latitude
    longi = data.longitude
    alti = data.altitude
    nav_data.append(Navstatus(lati, longi, alti, xacc, yacc, zacc))

def getMissionid(data):
    mission_id = data.data

def getTemp(data):
    temp = data.temperature
    temp_data.append(temp)
    

if __name__ == '__main__':
    
    ros_start("sensorhandler")
    rate = rospy.Rate(10)

    rospy.Subscriber("/ground/servoCom", String, getMission)
    rospy.Subscriber("/ground/request", String, request)
    rospy.Subscriber("/ground/mission", String, request)
    rospy.Subscriber("/mavros/imu/data", Imu, ImuData)
    rospy.Subscriber("/mavros/navsatfix/data", NavSatFix, getNavData)
    rospy.Subscriber("/mavros/batterystate/data", BatteryState, getBatData)
    rospy.Subscriber("/mavros/temperature/data", Temperature, getTemp)
    rospy.Subscriber(mavros.get_topic('state'), State, state_cb)

    rospy.spin()
