import RPi.GPIO as GPIO
import rospy
import mavros
import mavros_msgs
import nav_msgs
from std_msgs.msg import String
from sensor_msgs.msg import Imu, NavSatFix, NavSatStatus
import math

#It should be changed on the release.Because it might be the same port when pixhawk connected
servoPin = 17
 # GPIO 17 for PWM with 50Hz (it depends on servo motor)
p = GPIO.PWM(servoPin, 50)

rate = rospy.Rate(10)

isRotated = False
current_mission = 0
mission_data = []
lastlat = 0
lastlon = 0
lastalt = 0
lat = 0
lon = 0
alt = 0
xaccel = 0
yaccel = 0
zaccel = 0
#Should be getted from mission data

class Mission:
    def __init__(self, mission_id, cycle, lat, lon, height, weight):
        self.mission_id = mission_id
        self.cycle = cycle
        self.lat = lat
        self.lon = lon
        self.height = height
        self.weight = weight


#Cycle should be int.Therefore be aware of what data you are passing from ros
def rotate_by_value(cycle):
    p.ChangeDutyCycle(cycle)

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

pub = rospy.Publisher('/rpi/mission/servoCom', String, queue_size=20, subscriber_listener=subscriberListener())


def ros_start(node):
    rospy.init_node(node , anonymous=True)
   

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

def getNavData(data):
    lat = data.latitude
    lon = data.longitude
    alt = data.altitude
    #If any parameter changes,calculate function will be triggered
    calculate(lat, lon, alt, xaccel, yaccel, zaccel)

def getAcceleration(data):
    xaccel, yaccel, zaccel = data.linear_acceleration.x, data.linear_acceleration.y, data.linear_acceleration.z
    calculate(lat, lon, alt, xaccel, yaccel, zaccel)

def calculate(lat, lon, alt, xac, yac, zac):
    for i, c, x, y, z, w in mission_data:
        xtime = abs(x - lat) / xac
        ytime = abs(y - lon) / yac

        #This not required but I added that because of after takeoff calculations
        #Locations can be measured from sea level and some coordinates is greater than 
        #actual position.I want to avoid that error.
        ztime = (abs(alt - z) / zac) + (abs(alt - z)/w*9.8)

        totaltime = math.sqrt(xtime**2 + ytime**2 + ztime**2)
        
        line1 = abs(0-math.sqrt(x**2 + y**2))
        line2 = abs(0-math.sqrt(x**2 + y**2))
        degree = math.asin(math.sqrt(line1**2 + line2**2))

        if degree == 90 or degree == 270 and totaltime < 15:
            rotate_by_value(c)
            rospy.loginfo("Mission '{}' weight dropped".format(i))
            mission_data.remove(Mission(i, c, x, y, z, w))
        elif degree > 90 and degree < 270 and totaltime < 20:
            rotate_by_value(c)
            rospy.loginfo("Mission '{}' weight dropped".format(i))
            mission_data.remove(Mission(i, c, x, y, z, w))


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
    GPIO.setwarnings(False)
    p.start(2.5)

    ros_start("servo")
    rospy.Subscriber("/ground/mission/servoCom", String, getMission)
    rospy.Subscriber("/mavros/navsatfix", NavSatFix, getNavData)
    rospy.Subscriber("/mavros/imu/data", Imu, getAcceleration)


    rospy.spin()

