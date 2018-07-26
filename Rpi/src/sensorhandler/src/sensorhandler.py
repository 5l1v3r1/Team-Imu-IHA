import rospy
import mavros
import mavros_msgs
import nav_msgs
from std_msgs.msg import String
from sensor_msgs.msg import Imu, NavSatFix, NavSatStatus

pub = rospy.Publisher('/rpi/sensorhandler', String, queue_size=20, subscriber_listener=subscriberListener())
lat = 0
lon = 0
alt = 0
xac = 0
yac = 0
zac = 0
pressure = 0
flightMode = 0
flightTime = " "
escTemp = 0
circuitTemp = 0
batteryTemp = 0
currentConsump = 0
motor_cycle = 0
error_info = ""
flight_remaining = 0
mission_info = ""
roll , pitch, yaw = 0, 0, 0
batt = ""
wind = 0

pub = rospy.Publisher('/rpi/servoCom', String, queue_size=20, subscriber_listener=subscriberListener())

class Mission:
    def __init__(self, mission_id, cycle, lat, lon, height, weight):
        self.mission_id = mission_id
        self.cycle = cycle
        self.lat = lat
        self.lon = lon
        self.height = height
        self.weight = weight

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

def ros_start(node):
    rospy.init_node(node , anonymous=True)

def request(data):


def sendStatus():

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
    xac, yac, zac = data.linear_acceleration.x, data.linear_acceleration.y, data.linear_acceleration.z


def getNavData(data):
    lat = data.latitude
    lon = data.longitude
    alt = data.altitude
    #If any parameter changes,calculate function will be triggered
    calculate(lat, lon, alt, xaccel, yaccel, zaccel)




if __name__ = '__main__':
    
    ros_start("sensorhandler")
    rate = rospy.Rate(10)

    rospy.Subscriber("/ground/servoCom", String, getMission)
    rospy.Subscriber("/ground/request", String, request)
    rospy.Subscriber("/mavros/imu/data", Imu, ImuData)
    rospy.Subscriber("/mavros/navsatfix", NavSatFix, getNavData)

    rospy.spin()
